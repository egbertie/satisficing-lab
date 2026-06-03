const COS = require('cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: 'AKIDVpvmOgkZ9VdW9Xf4E9qIVTCg5NlBatzr', SecretKey: 'f5GDwPf2DAuROBq5KSN9vXwEJBpJdqxv' });
const buckets = ['6949-static-myj-7gfpdg2u496ece2b-1329275403', '6d79-myj-7gfpdg2u496ece2b-1329275403'];
const regions = ['ap-guangzhou','ap-beijing','ap-shanghai','ap-nanjing','ap-chengdu','ap-hongkong'];

(async () => {
  for (const b of buckets) {
    for (const r of regions) {
      try {
        await cos.headBucket({ Bucket: b, Region: r });
        console.log(`Bucket: ${b} => Region: ${r} (OK)`);
        break;
      } catch (e) {
        if (e.statusCode === 403) {
          console.log(`Bucket: ${b} => Region: ${r} (OK, 403=存在)`);
          break;
        }
      }
    }
  }
})();
