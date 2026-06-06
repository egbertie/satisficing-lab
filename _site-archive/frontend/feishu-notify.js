/**
 * 飞书通知 SDK v1.0
 * 满意解研究所 · 客户通道前端
 */
const FEISHU_CONFIG = {
  webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/10cdb92c-ee3f-479c-85b4-78144c9988c8",
  bitableFormUrl: "https://gcngtm4k2m6u.feishu.cn/base/ErBVb6ZHqaFXcvsFlHxcXp8Enjd?table=tblG65JNbsbAVpjp&view=vewFaVgAZW",
  bitableUrl: "https://gcngtm4k2m6u.feishu.cn/base/ErBVb6ZHqaFXcvsFlHxcXp8Enjd"
};
async function feishuSendText(t){try{const r=await fetch(FEISHU_CONFIG.webhook,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({msg_type:"text",content:{text:t}})});return(await r.json()).code===0}catch(e){return!1}}
async function feishuSendPost(t,c){try{const r=await fetch(FEISHU_CONFIG.webhook,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({msg_type:"post",content:{post:{zh_cn:{title:t,content:[c]}}}})});return(await r.json()).code===0}catch(e){return!1}}
async function feishuNotifyContact(d){const n=new Date().toLocaleString("zh-CN",{timeZone:"Asia/Shanghai"});return feishuSendPost("🔔 满意解研究所 · 新客户留言",[{tag:"text",text:"📬 新的客户留言\n\n"},{tag:"text",text:"👤 姓名："+(d.name||"未填")+"\n"},{tag:"text",text:"📧 邮箱："+(d.email||"未填")+"\n"},{tag:"text",text:"🏢 企业："+(d.company||"未填")+"\n"},{tag:"text",text:"💬 留言："+(d.message||"未填")+"\n\n"},{tag:"text",text:"⏰ 时间："+n+"\n"},{tag:"a",text:"📊 查看客户数据表",href:FEISHU_CONFIG.bitableUrl}])}
async function feishuNotifyRegister(d){const n=new Date().toLocaleString("zh-CN",{timeZone:"Asia/Shanghai"});return feishuSendPost("🎉 满意解研究所 · 新客户注册",[{tag:"text",text:"🎉 新客户注册\n\n"},{tag:"text",text:"👤 姓名："+(d.name||"未填")+"\n"},{tag:"text",text:"📧 邮箱："+(d.email||"未填")+"\n"},{tag:"text",text:"📱 手机："+(d.phone||"未填")+"\n"},{tag:"text",text:"🏢 企业："+(d.company||"未填")+"\n"},{tag:"text",text:"💼 职位："+(d.position||"未填")+"\n"},{tag:"text",text:"🔬 赛道："+(d.industry||"未填")+"\n"},{tag:"text",text:"🌱 阶段："+(d.stage||"未填")+"\n"},{tag:"text",text:"📥 来源："+(d.source||"未填")+"\n"},{tag:"text",text:"⭐ 关注："+(d.interests||"未填")+"\n\n"},{tag:"text",text:"⏰ 时间："+n+"\n"},{tag:"a",text:"📊 查看客户数据表",href:FEISHU_CONFIG.bitableUrl}])}
window.FeishuNotify={sendText:feishuSendText,sendPost:feishuSendPost,contact:feishuNotifyContact,register:feishuNotifyRegister,config:FEISHU_CONFIG};
