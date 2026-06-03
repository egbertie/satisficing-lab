"""
时间晶体存储系统
混合架构：Kùzu（图）+ Chroma（向量）+ SQLite（元数据）
为绕过Chroma默认ONNX模型下载，使用轻量哈希向量嵌入
"""

import json
import sqlite3
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

import chromadb
import kuzu

from base.crystal_models import TemporalCrystal


class SimpleEmbeddingFunction:
    """
    改进型轻量哈希向量嵌入函数 (n-gram版)
    在零下载的前提下，用bigram/trigram替代单字哈希，显著提升语义精度
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

    def _token_ngrams(self, text: str, n_list=[1, 2, 3]) -> List[str]:
        """提取字符级n-gram，保留局部语义结构"""
        text = text.lower()
        ngrams = []
        for n in n_list:
            for i in range(len(text) - n + 1):
                ngrams.append(text[i:i + n])
        return ngrams

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dim, dtype=np.float32)
            ngrams = self._token_ngrams(text)
            for i, ng in enumerate(ngrams):
                idx = (hash(ng) + i * 31) % self.dim
                vec[idx] += 1.0
            # 对数压缩高频维度，防止少数n-gram主导
            vec = np.sign(vec) * np.log1p(np.abs(vec))
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self._embed_texts(input)

    def embed_documents(self, input: List[str]) -> List[List[float]]:
        return self._embed_texts(input)

    def embed_query(self, input: str) -> List[float]:
        return self._embed_texts([input])[0]

    def name(self) -> str:
        return "ngram_hash_v2"

    def dict(self) -> Dict:
        return {"name": self.name(), "dim": self.dim}


class TemporalCrystalStore:
    """
    时间晶体仓库
    支持因果查询、叙事重构、记忆巩固
    """

    def __init__(self,
                 db_path: str = "./data/temporal"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Kùzu 图数据库（文件路径）
        kuzu_file = str(self.db_path / "kuzu_graph.db")
        self.kuzu_db = kuzu.Database(kuzu_file)
        self.kuzu_conn = kuzu.Connection(self.kuzu_db)
        self._init_graph_schema()

        # Chroma 向量库（不使用默认嵌入函数，手动传递向量，避免下载ONNX模型）
        self.chroma_client = chromadb.PersistentClient(path=str(self.db_path / "chroma"))
        self.embedding_fn = SimpleEmbeddingFunction(dim=384)
        self.vector_collection = self.chroma_client.get_or_create_collection(
            name="temporal_vectors",
            metadata={"hnsw:space": "cosine"}
        )

        # SQLite 元数据
        self.sqlite_conn = sqlite3.connect(str(self.db_path / "metadata.db"))
        self._init_sqlite_schema()

    def _init_graph_schema(self):
        """初始化图结构"""
        schemas = [
            "CREATE NODE TABLE IF NOT EXISTS Event(event_id STRING, timestamp TIMESTAMP, semantic_time STRING, event_type STRING, content STRING, strength DOUBLE, narrative_cluster STRING, PRIMARY KEY(event_id))",
            "CREATE NODE TABLE IF NOT EXISTS Crystal(crystal_id STRING, compression_ratio DOUBLE, created_at TIMESTAMP, PRIMARY KEY(crystal_id))",
            "CREATE REL TABLE IF NOT EXISTS CAUSED(FROM Event TO Event, MANY_MANY)",
            "CREATE REL TABLE IF NOT EXISTS REFERENCES(FROM Event TO Crystal, MANY_MANY)",
            "CREATE REL TABLE IF NOT EXISTS EVOLVED_FROM(FROM Crystal TO Crystal, MANY_MANY)"
        ]
        for schema in schemas:
            try:
                self.kuzu_conn.execute(schema)
            except Exception as e:
                if "already exists" not in str(e).lower():
                    raise

    def _init_sqlite_schema(self):
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_events (
                event_id TEXT PRIMARY KEY,
                timestamp REAL,
                semantic_time TEXT,
                event_type TEXT,
                content TEXT,
                crystal_refs TEXT,
                causal_parents TEXT,
                narrative_cluster TEXT,
                strength REAL,
                access_count INTEGER DEFAULT 0
            )
        """)
        self.sqlite_conn.commit()

    def store_event(self, crystal: TemporalCrystal):
        """存储事件到三层存储"""
        # 1. Kùzu - 注意字符串转义
        content_escaped = crystal.content.replace("'", "''")[:1000]
        query = f"""
            CREATE (e:Event {{
                event_id: '{crystal.event_id}',
                timestamp: timestamp('{crystal.timestamp.isoformat()}'),
                semantic_time: '{crystal.semantic_time}',
                event_type: '{crystal.event_type}',
                content: '{content_escaped}',
                strength: {crystal.strength},
                narrative_cluster: '{crystal.narrative_cluster}'
            }})
        """
        self.kuzu_conn.execute(query)

        # 建立因果边
        for parent_id in crystal.causal_parents:
            edge_query = f"""
                MATCH (e1:Event {{event_id: '{parent_id}'}}), (e2:Event {{event_id: '{crystal.event_id}'}})
                CREATE (e1)-[:CAUSED]->(e2)
            """
            try:
                self.kuzu_conn.execute(edge_query)
            except Exception:
                pass

        # 2. Chroma（手动传递嵌入向量）
        embedding = self.embedding_fn.embed_query(crystal.content)
        self.vector_collection.add(
            ids=[crystal.event_id],
            documents=[crystal.content],
            embeddings=[embedding],
            metadatas=[{
                "timestamp": crystal.timestamp.isoformat(),
                "narrative_cluster": crystal.narrative_cluster,
                "event_type": crystal.event_type
            }]
        )

        # 3. SQLite
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO temporal_events
            (event_id, timestamp, semantic_time, event_type, content, crystal_refs, causal_parents, narrative_cluster, strength)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crystal.event_id,
            crystal.timestamp.timestamp(),
            crystal.semantic_time,
            crystal.event_type,
            crystal.content,
            json.dumps(crystal.crystal_refs),
            json.dumps(crystal.causal_parents),
            crystal.narrative_cluster,
            crystal.strength
        ))
        self.sqlite_conn.commit()

    def query_causal_chain(self, event_id: str, direction: str = "both", depth: int = 3) -> List[Dict]:
        """因果链查询"""
        if direction == "backward":
            query = f"""
                MATCH (e:Event {{event_id: '{event_id}'}})<-[:CAUSED*1..{depth}]-(ancestor:Event)
                RETURN ancestor.event_id, ancestor.content, ancestor.timestamp
                ORDER BY ancestor.timestamp
            """
        elif direction == "forward":
            query = f"""
                MATCH (e:Event {{event_id: '{event_id}'}})-[:CAUSED*1..{depth}]->(descendant:Event)
                RETURN descendant.event_id, descendant.content, descendant.timestamp
                ORDER BY descendant.timestamp
            """
        else:
            query = f"""
                MATCH (e:Event {{event_id: '{event_id}'}})<-[:CAUSED*1..{depth}]-(ancestor:Event)
                RETURN ancestor.event_id as id, ancestor.content as content, 'cause' as type
                UNION
                MATCH (e:Event {{event_id: '{event_id}'}})-[:CAUSED*1..{depth}]->(descendant:Event)
                RETURN descendant.event_id as id, descendant.content as content, 'effect' as type
            """
        result = self.kuzu_conn.execute(query)
        try:
            df = result.get_as_df()
            return df.to_dict('records')
        except Exception:
            records = []
            while result.has_next():
                records.append(dict(zip(result.get_column_names(), result.get_next())))
            return records

    def semantic_query(self, query_text: str, narrative_filter: Optional[str] = None, top_k: int = 5) -> List[TemporalCrystal]:
        """语义搜索 + 元数据过滤"""
        kwargs = {}
        if narrative_filter:
            kwargs["where"] = {"narrative_cluster": narrative_filter}

        query_embedding = self.embedding_fn.embed_query(query_text)
        results = self.vector_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            **kwargs
        )

        events = []
        if not results or not results.get("ids") or not results["ids"]:
            return events
        for event_id in results["ids"][0]:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT * FROM temporal_events WHERE event_id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                events.append(self._row_to_crystal(row))
        return events

    def _row_to_crystal(self, row) -> TemporalCrystal:
        """数据库行转对象"""
        return TemporalCrystal(
            event_id=row[0],
            timestamp=datetime.fromtimestamp(row[1]),
            semantic_time=row[2],
            event_type=row[3] if row[3] else "perception",
            content=row[4],
            crystal_refs=json.loads(row[5]) if row[5] else [],
            causal_parents=json.loads(row[6]) if row[6] else [],
            narrative_cluster=row[7],
            strength=row[8] if row[8] is not None else 1.0,
            access_count=row[9] if len(row) > 9 else 0
        )

    def consolidate_memory(self, cluster: str):
        """记忆巩固"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT * FROM temporal_events
            WHERE narrative_cluster = ?
            ORDER BY timestamp
        """, (cluster,))
        rows = cursor.fetchall()

        if len(rows) < 5:
            return

        summary_content = f"[记忆整合] 叙事簇'{cluster}'在{len(rows)}个事件后形成稳定模式"
        summary_event = TemporalCrystal(
            semantic_time=f"{cluster}-整合期",
            event_type="reflection",
            content=summary_content,
            narrative_cluster=cluster,
            causal_parents=[row[0] for row in rows[-3:]]
        )
        self.store_event(summary_event)

        for row in rows:
            cursor.execute("""
                UPDATE temporal_events SET strength = MIN(1.0, strength + 0.1)
                WHERE event_id = ?
            """, (row[0],))
        self.sqlite_conn.commit()
