# 🎨 文生图提示词库（Image Prompts Library）

所有提示词已针对 Midjourney v6、DALL-E 3、Stable Diffusion XL 优化。

---

## 📌 全局风格基底

**必须附加在所有提示词末尾**：

```
soft watercolor illustration, children's book style, warm golden light, 
detailed magical background, Studio Ghibli inspired, Hayao Miyazaki aesthetic,
whimsical atmosphere, high quality, 4k resolution, storybook art, 
rich colors, gentle brush strokes, dreamy and enchanting
```

---

## 👥 主角组合场景提示词

### 阿奇独自冒险

```
young wizard boy Archi, silver messy hair, round wire glasses, dark blue starry robe, 
warm smile, slightly oversized robe, 10 years old, standing in [场景], 
looking with curiosity and wonder, chibi anime style, [全局风格基底]
```

### 阿奇与露娜对话

```
young wizard boy Archi with silver hair and blue starry robe, 
small fairy girl Luna with long white hair and book-page wings glowing blue, 
both in [场景], Luna pointing upward as if explaining, Archi looking amazed,
magical conversation atmosphere, [全局风格基底]
```

### 阿奇与小铁博士实验

```
young wizard boy Archi watching with wide eyes, tiny round bronze robot Dr.Teto 
in miniature lab coat operating tiny equipment, colorful experimental effects, 
smoke and sparkles, [实验场景], fun and energetic mood, [全局风格基底]
```

### 四人全员集合

```
young wizard Archi, fairy Luna with book wings, tiny robot Dr.Teto, 
teenage adventurer Akagi in red cloak, all four characters together in [场景], 
team composition, each with distinct personality expression, [全局风格基底]
```

---

## 🗺️ 场景封面提示词

### 无限图书馆

```
infinite magical library, endless bookshelves reaching into glowing clouds, 
warm amber and gold lighting, floating open books, spiral staircase, 
ancient tree in center radiating golden light, dust motes dancing, 
sense of infinite knowledge and wonder, [全局风格基底]
```

### 元素火山群岛

```
archipelago of volcanic islands, each island glowing different elemental colors,
colorful gas clouds floating between islands, crystal mineral formations, 
chemistry flask shaped mountains, elemental spirits dancing in flames,
spectacular and colorful, aerial view, [全局风格基底]
```

### 星算塔楼

```
cluster of tall magical towers floating above clouds at night,
golden mathematical equations forming bridges between towers,
starry sky background, number spirits like fireflies, 
telescope pointing at constellation, glowing geometric patterns,
mystical and intellectual atmosphere, [全局风格基底]
```

### 生命迷宫森林

```
giant bioluminescent forest where trees are enormous cells,
DNA double helix vines glowing green and blue, 
mitochondria as glowing lanterns, nucleus as a glowing shrine inside trees,
microscopic world at macro scale, ethereal and alive,
soft green and blue glow, [全局风格基底]
```

### 时光回廊

```
infinite corridor stretching into warm amber distance,
doorways on both sides each showing different historical eras,
floating portrait frames of historical figures,
ancient maps and artifacts floating, time portal shimmer effects,
warm nostalgic atmosphere, [全局风格基底]
```

### 荣耀圣殿

```
grand golden temple on cloud-covered mountaintop,
celestial light beams shining down, Nobel medal motifs on architecture,
portrait gallery of famous scientists visible through columns,
reverent and inspiring atmosphere, [全局风格基底]
```

---

## 📖 知识点场景提示词

### 化学反应发生时

```
two colorful elemental spirits reaching toward each other and merging,
explosion of light and color as they combine,
new combined spirit emerging from the reaction,
chemistry magic aesthetic, laboratory setting with magical twist, [全局风格基底]
```

### DNA/遗传密码

```
glowing DNA double helix as a grand staircase,
tiny characters climbing the steps reading genetic code letters A T G C,
helix forming an archway into a glowing library,
biological blueprint aesthetic, microscopic and magical, [全局风格基底]
```

### 牛顿力学/物理定律

```
objects floating and moving in magical patterns following invisible rules,
golden force lines and motion trails visible,
apple falling and creating ripple effect of discovery,
physics made visible as colorful energy lines, [全局风格基底]
```

### 历史时代门开启

```
ornate door opening to reveal historical era beyond,
warm light pouring through doorway showing historical scene,
character silhouette at threshold looking into the past,
time travel portal effect, dramatic lighting, [全局风格基底]
```

### 数学顿悟时刻

```
character surrounded by floating equations that suddenly align perfectly,
golden light emanating from mathematical formula,
puzzle pieces clicking together as glowing numbers,
eureka moment visualization, brilliant and clear, [全局风格基底]
```

### 诺贝尔科学家实验室

```
historical scientist in magical workshop version of laboratory,
scientific discovery moment with dramatic lighting,
experiment glowing with breakthrough energy,
real-world science aestheticized as magic, portrait-style composition, [全局风格基底]
```

---

## 🃏 卡牌游戏专用提示词

### 知识英雄卡背景

```
trading card illustration, heroic portrait composition,
character in dynamic pose, knowledge domain themed background,
card frame with ornate magical border, gold trim,
collectible card game aesthetic, [全局风格基底]
```

### 场景探险卡背景

```
landscape card illustration, wide establishing shot,
knowledge domain environment as adventure location,
atmospheric and inviting, card game scene card format,
horizontal composition with sky and ground, [全局风格基底]
```

### 知识宝石卡

```
glowing gemstone in center, knowledge symbol reflected inside gem,
magical sparkles and light rays, dark rich background to make gem pop,
collectible item card aesthetic, precious and rare feeling, [全局风格基底]
```

---

## ⚠️ 角色一致性提示（重要）

**每次生成角色图时，在提示词最前面加入以下「角色锁定词」确保外观一致**：

```
[CHARACTER CONSISTENCY LOCK]
Archi: silver messy hair, round wire glasses, dark blue starry robe, age 10, warm smile
Luna: long white hair, book-page wings, pale glowing skin, blue aura, small fairy
Dr.Teto: round bronze robot body, monocle left eye, white lab coat, 20cm tall
Akagi: short black hair, red travel cloak, teenage, wise expression, journal at waist
[same character design as previous images, consistent appearance]
```

**进阶技巧**：若使用支持图生图功能的平台（如Midjourney的--cref参数），上传已满意的角色参考图，可大幅提升跨图一致性。
