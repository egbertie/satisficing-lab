const COS = require('cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: 'AKIDVpvmOgkZ9VdW9Xf4E9qIVTCg5NlBatzr', SecretKey: 'f5GDwPf2DAuROBq5KSN9vXwEJBpJdqxv' });
const Bucket = '6949-static-myj-7gfpdg2u496ece2b-1329275403';
const Region = 'ap-shanghai';
const Key = 'test/skillhub-verification-' + Date.now() + '.txt';
const Body = Buffer.from('Kimi Claw - SkillHub COS verification test at ' + new Date().toISOString());
cos.putObject({ Bucket, Region, Key, Body }, function(err, data) {
  if (err) {
    console.error(JSON.stringify({ success: false, error: err.message }));
    process.exit(1);
  }
  const location = 'https://' + Bucket + '.cos.' + Region + '.myqcloud.com/' + Key;
  console.log(JSON.stringify({ success: true, bucket: Bucket, region: Region, key: Key, etag: data.ETag, location: location }));
});
