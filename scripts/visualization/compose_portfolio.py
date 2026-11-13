from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

HERE=Path(__file__).parent
ROOT=HERE.resolve().parents[1]
FONT=Path('C:/Windows/Fonts')

def font(size,bold=False,latin=False):
    name=('segoeuib.ttf' if bold else 'segoeui.ttf') if latin else ('msyhbd.ttc' if bold else 'msyh.ttc')
    return ImageFont.truetype(str(FONT/name),size)

def poster(mode,title,number,subtitle,notes):
    canvas=Image.new('RGBA',(1920,1280),'#f0f3f5')
    model=Image.open(HERE/f'{mode}-raw.png').convert('RGBA')
    # Fade only the image boundary, outside the CAD silhouette, to blend floor shadows.
    mask=Image.new('L',model.size,255)
    md=ImageDraw.Draw(mask)
    for i in range(90):
        md.rectangle((i,i,model.width-1-i,model.height-1-i),outline=round(255*i/90))
    model.putalpha(ImageChops.multiply(model.getchannel('A'),mask))
    model=model.resize((1250,1250),Image.Resampling.LANCZOS)
    canvas.alpha_composite(model,(590,-20 if mode=='exploded' else -10))
    draw=ImageDraw.Draw(canvas)
    ink='#1c3043'; muted='#6c7b87'; gold='#b77b36'
    draw.line((80,79,1840,79),fill='#c6cfd5',width=2)
    draw.text((80,31),'MECHANICAL ENGINEERING / CAD PORTFOLIO',font=font(24,latin=True),fill=muted)
    draw.text((1510,31),'COURSE PROJECT · 2026',font=font(23,latin=True),fill=muted)
    draw.text((80,126),title,font=font(72,bold=True),fill=ink)
    draw.text((83,228),subtitle,font=font(25,latin=True),fill=muted)
    draw.rectangle((80,427,124,432),fill=gold)
    draw.text((80,455),number,font=font(100,latin=True),fill=ink)
    draw.text((83,594),notes[0],font=font(34,bold=True),fill=ink)
    draw.text((83,655),notes[1],font=font(25),fill=muted)
    draw.text((83,697),notes[2],font=font(25),fill=muted)
    draw.line((80,1167,1840,1167),fill='#c6cfd5',width=2)
    draw.text((80,1200),'HUANG ZIJIE / 黄子杰',font=font(24),fill=ink)
    draw.text((700,1200),'SOURCE: ORIGINAL STEP · 43 SOLIDS',font=font(23,latin=True),fill=muted)
    draw.text((1380,1200),'展示配色不代表实际材料',font=font(23),fill=muted)
    target=ROOT/'assets'/f'{mode}-render.png'
    canvas.convert('RGB').save(target,optimize=True)
    print(target)

poster('assembly','落料拉深复合模','01','BLANKING & DEEP DRAWING COMPOUND DIE',
       ['装配整体','保留模型原始装配位置','重新设置视角、材质与光照'])
poster('exploded','分层结构展示','02','LAYERED ASSEMBLY / EXPLODED PRESENTATION',
       ['由整体到内部','各组沿工作方向平移','展示间距不代表实际行程'])
poster('section','工作区剖切','03','SECTION THROUGH THE TOOLING AXIS',
       ['内部配合关系','基于 STEP 实体布尔截取','暖色标示新生成的剖切面'])
