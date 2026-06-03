// zero_pool_loader - io_uring + ZeroPool implementation
// Target: Checkpoint loading 3.8x acceleration

#include <iostream>
#include <vector>
#include <chrono>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>

// io_uring headers (Linux 5.10+)
#include <liburing.h>

class ZeroPoolLoader {
private:
    std::vector<char> memory_pool;
    struct io_uring ring;
    size_t pool_size;
    
public:
    ZeroPoolLoader(size_t size = 512 * 1024 * 1024) : pool_size(size) {
        // Pre-allocate memory pool to eliminate malloc during I/O
        memory_pool.resize(pool_size);
        
        // Initialize io_uring with queue depth 256
        int ret = io_uring_queue_init(256, &ring, 0);
        if (ret < 0) {
            throw std::runtime_error("io_uring init failed");
        }
        
        std::cout << "ZeroPool initialized: " << pool_size / (1024*1024) << "MB pool" << std::endl;
    }
    
    ~ZeroPoolLoader() {
        io_uring_queue_exit(&ring);
    }
    
    // Load checkpoint using io_uring + ZeroPool
    size_t load_checkpoint(const char* filepath) {
        int fd = open(filepath, O_RDONLY);
        if (fd < 0) {
            perror("open");
            return 0;
        }
        
        // Get file size
        struct stat st;
        fstat(fd, &st);
        size_t file_size = st.st_size;
        
        // Memory map the file (zero-copy)
        void* mapped = mmap(nullptr, file_size, PROT_READ, MAP_PRIVATE, fd, 0);
        if (mapped == MAP_FAILED) {
            perror("mmap");
            close(fd);
            return 0;
        }
        
        // Submit read requests via io_uring (batch processing)
        const size_t chunk_size = 64 * 1024; // 64KB chunks
        size_t num_chunks = (file_size + chunk_size - 1) / chunk_size;
        
        for (size_t i = 0; i < num_chunks; i++) {
            size_t offset = i * chunk_size;
            size_t bytes_to_read = std::min(chunk_size, file_size - offset);
            
            // Use pre-allocated memory pool
            char* dest = memory_pool.data() + (offset % pool_size);
            
            struct io_uring_sqe* sqe = io_uring_get_sqe(&ring);
            if (!sqe) {
                // Submit queue full, flush and retry
                io_uring_submit(&ring);
                sqe = io_uring_get_sqe(&ring);
            }
            
            io_uring_prep_read(sqe, fd, dest, bytes_to_read, offset);
            io_uring_sqe_set_data(sqe, (void*)offset);
        }
        
        // Submit all requests
        io_uring_submit(&ring);
        
        // Wait for completions
        size_t completed = 0;
        while (completed < num_chunks) {
            struct io_uring_cqe* cqe;
            int ret = io_uring_wait_cqe(&ring, &cqe);
            if (ret < 0) continue;
            
            if (cqe->res < 0) {
                std::cerr << "Read error: " << strerror(-cqe->res) << std::endl;
            } else {
                completed++;
            }
            
            io_uring_cqe_seen(&ring, cqe);
        }
        
        // Cleanup
        munmap(mapped, file_size);
        close(fd);
        
        std::cout << "Loaded " << file_size / (1024*1024) << "MB in " 
                  << num_chunks << " chunks" << std::endl;
        
        return file_size;
    }
    
    // Get pool memory for direct access
    char* get_pool() {
        return memory_pool.data();
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <checkpoint_file>" << std::endl;
        return 1;
    }
    
    try {
        ZeroPoolLoader loader;
        
        auto start = std::chrono::high_resolution_clock::now();
        size_t loaded = loader.load_checkpoint(argv[1]);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "Loaded " << loaded << " bytes in " << duration.count() << " ms" << std::endl;
        if (loaded > 0) {
            std::cout << "Throughput: " << (loaded / 1024.0 / 1024.0) / (duration.count() / 1000.0) 
                      << " MB/s" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
