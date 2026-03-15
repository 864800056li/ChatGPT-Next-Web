const { postMoment } = require('../bot');

// 朋友圈内容库
const momentContents = {
  // 创业感悟
  startup: [
    "创业就是不断解决问题的过程，每个困难都是成长的机会。💪",
    "今天又是一个12小时的工作日，但看到产品一点点成型，值了。🔥",
    "团队又攻克了一个技术难题，这种成就感无法替代。🚀",
    "创业路上最宝贵的不是钱，是和你一起熬夜的伙伴。❤️",
    "从0到1很难，但从1到100更难。保持初心，继续前行。✨"
  ],
  
  // 生活分享
  life: [
    "忙了一周，终于有时间喝杯咖啡。简单的幸福。☕",
    "早起的感觉真好，城市还没醒，我已经开始奔跑。🌅",
    "运动是唯一的解药，5公里跑完，思路都清晰了。🏃",
    "周末陪家人，工作再忙也不能忘了生活。👨‍👩‍👧",
    "一本好书，一杯茶，难得的安静时光。📚"
  ],
  
  // 行业观察
  insight: [
    "AI正在改变每一个行业，不进则退。保持学习，保持好奇。🤖",
    "用户的需求永远是对的，产品要围绕用户转。🎯",
    "技术只是手段，价值才是目的。别为了技术而技术。💡",
    "这个时代，执行力比想法更重要。想得再好，不如先做。⚡",
    "竞争不是打败对手，而是服务好用户。专注自己，其他的交给时间。🌱"
  ],
  
  // 正能量
  positive: [
    "相信过程，结果自然不会差。🌟",
    "每一个不曾起舞的日子，都是对生命的辜负。💃",
    "困难是暂时的，放弃是永远的。坚持住！💪",
    "你的努力，时间看得见。⏰",
    "不要等准备好了才开始，开始了才会准备好。🚀"
  ]
};

// 获取今日内容
function getTodayContent() {
  const date = new Date();
  const dayOfWeek = date.getDay();
  const dayOfMonth = date.getDate();
  
  // 根据日期选择类别
  const categories = Object.keys(momentContents);
  const categoryIndex = dayOfMonth % categories.length;
  const category = categories[categoryIndex];
  
  // 从类别中随机选一条
  const contents = momentContents[category];
  const contentIndex = Math.floor(Math.random() * contents.length);
  
  return contents[contentIndex];
}

// 发朋友圈
async function main() {
  const content = getTodayContent();
  console.log(`准备发朋友圈: ${content}`);
  
  const success = await postMoment(content);
  
  if (success) {
    console.log('✅ 朋友圈发送成功');
    process.exit(0);
  } else {
    console.log('❌ 朋友圈发送失败');
    process.exit(1);
  }
}

main();
