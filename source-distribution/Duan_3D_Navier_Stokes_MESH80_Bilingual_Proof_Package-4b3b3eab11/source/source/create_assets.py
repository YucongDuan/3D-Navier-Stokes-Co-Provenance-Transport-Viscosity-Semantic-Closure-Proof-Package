from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib import font_manager

OUT=Path('/mnt/data/navier_mesh80_work/figures')
OUT.mkdir(parents=True, exist_ok=True)
FONT_CN='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_CN_B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
font_cn=font_manager.FontProperties(fname=FONT_CN)
font_cn_b=font_manager.FontProperties(fname=FONT_CN_B)

NAVY='#173A5E'; TEAL='#2B7A78'; GOLD='#C58F2B'; LIGHT='#EAF3F5'; CREAM='#FBF4E6'; RED='#B6493A'; GREY='#6B7C8C'; GREEN='#4D7C5A'; WHITE='#FFFFFF'

def save(fig,name):
    fig.savefig(OUT/name, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close(fig)

def box(ax,xy,w,h,text,fc=LIGHT,ec=NAVY,fontsize=13,fp=None,lw=1.5):
    x,y=xy
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.025',facecolor=fc,edgecolor=ec,linewidth=lw)
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fontsize,color=NAVY,fontproperties=fp,wrap=True)
    return p

def arrow(ax,start,end,color=GREY,rad=0,style='-|>',lw=1.5):
    a=FancyArrowPatch(start,end,arrowstyle=style,mutation_scale=14,linewidth=lw,color=color,connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(a)
    return a

# Figure 1: MESH80 network
for lang in ['cn','en']:
    fig,ax=plt.subplots(figsize=(10,5.7)); ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
    if lang=='cn':
        title='MESH8.0 五核心语义网与 Navier–Stokes 后生别名'; sub='所有路径开放，但目标内容不得自动补写；流体术语只在完整语义包之后出生。'; fp=font_cn; fpb=font_cn_b
        labels={'D':'同一来源\n同一流体身份','I':'显式差异\n位置·方向·尺度','K':'完整语义\n输运·黏性·压力闭合','W':'价值边界\n不造第三来源','P':'输入—输出\n初态→有限时刻状态'}
    else:
        title='The MESH8.0 Five-Core Network and Post-Semantic Navier–Stokes Aliases'; sub='All routes are open, but target content is never auto-filled; fluid terms are aliases born after a complete packet.'; fp=None; fpb=None
        labels={'D':'Same provenance\nOne fluid identity','I':'Explicit differences\nposition · direction · scale','K':'Complete semantics\ntransport · viscosity · pressure closure','W':'Value boundary\nno third source','P':'Input-output\ninitial state → finite-time state'}
    ax.text(5,5.55,title,ha='center',va='center',fontsize=18,color=NAVY,fontproperties=fpb,weight='bold')
    ax.text(5,5.12,sub,ha='center',va='center',fontsize=10.5,color=GREY,fontproperties=fp)
    pos={'D':(1.1,3.4),'I':(4.0,4.0),'K':(7.0,3.4),'W':(6.2,1.25),'P':(2.1,1.25)}
    colors={'D':LIGHT,'I':'#EDF6F3','K':'#EEF1F8','W':CREAM,'P':'#F0F4FA'}
    for k,(x,y) in pos.items(): box(ax,(x,y),2.0,1.0,f'{k}\n{labels[k]}',fc=colors[k],ec=TEAL if k in ['I','W'] else NAVY,fontsize=11.5,fp=fp)
    # 10 representative bidirectional arrows
    pairs=[('D','I'),('I','K'),('K','W'),('W','P'),('P','D'),('P','K')]
    for a,b in pairs:
        xa,ya=pos[a]; xb,yb=pos[b]
        arrow(ax,(xa+1,ya+0.5),(xb+1,yb+0.5),TEAL,rad=0.08,lw=1.4)
        arrow(ax,(xb+1,yb+0.38),(xa+1,ya+0.38),GOLD,rad=-0.08,lw=1.0)
    footer='概念别名：不可压缩流、输运、黏性、压力、光滑性' if lang=='cn' else 'Aliases: incompressible flow, transport, viscosity, pressure, smoothness'
    ax.text(5,0.35,footer,ha='center',va='center',fontsize=11.5,color=TEAL,fontproperties=fpb)
    save(fig,f'fig1_mesh80_network_{lang}.png')

# Figure 2: three roles
for lang in ['cn','en']:
    fig,ax=plt.subplots(figsize=(10,5.5)); ax.set_xlim(0,10); ax.set_ylim(0,5.8); ax.axis('off')
    if lang=='cn':
        fp=font_cn; fpb=font_cn_b; title='同一流体来源中的三种角色：输运、黏性与压力'; src='单一动量来源包\nD：同一流体身份'; t='输运\n只重新配置来源位置\n不创造独立来源'; v='黏性\n内生消解速度差异\n只暴露已包含关系'; p='压力\n闭合不可压缩约束\n不成为第三来源'; out='光滑有限时刻正常形\nP：可继续演化的完整输出'; note='三种角色不是三个本体极；它们是同一来源包内的显式核心路径。'
    else:
        fp=None; fpb=None; title='Three Roles Inside One Fluid Provenance: Transport, Viscosity, and Pressure'; src='Single momentum packet\nD: one fluid identity'; t='Transport\nrelocates provenance\ncreates no independent source'; v='Viscosity\nendogenously eliminates differences\nexposes only included relations'; p='Pressure\ncloses incompressibility\ndoes not become a third source'; out='Smooth finite-time normal form\nP: complete continuable output'; note='The three roles are not three ontological poles; they are explicit core routes inside one provenance packet.'
    ax.text(5,5.35,title,ha='center',fontsize=18,color=NAVY,fontproperties=fpb,weight='bold')
    box(ax,(0.5,2.25),2.0,1.15,src,fc=CREAM,ec=GOLD,fontsize=12,fp=fp)
    box(ax,(3.05,3.6),2.1,1.25,t,fc=LIGHT,ec=TEAL,fontsize=11.2,fp=fp)
    box(ax,(3.05,1.95),2.1,1.25,v,fc='#EDF6F3',ec=GREEN,fontsize=11.2,fp=fp)
    box(ax,(3.05,0.3),2.1,1.25,p,fc='#EEF1F8',ec=NAVY,fontsize=11.2,fp=fp)
    box(ax,(7.2,2.05),2.25,1.5,out,fc='#F2F7F6',ec=TEAL,fontsize=11.5,fp=fp)
    for yy in [4.2,2.55,0.95]: arrow(ax,(2.5,2.82),(3.05,yy),GREY,lw=1.3)
    for yy in [4.2,2.55,0.95]: arrow(ax,(5.15,yy),(7.2,2.82),GREY,lw=1.3)
    ax.text(5,0.02,note,ha='center',va='bottom',fontsize=10.5,color=GREY,fontproperties=fp)
    save(fig,f'fig2_roles_{lang}.png')

# Figure 3: singularity triad
for lang in ['cn','en']:
    fig,ax=plt.subplots(figsize=(10,5.2)); ax.set_xlim(0,10); ax.set_ylim(0,5.4); ax.axis('off')
    if lang=='cn':
        fp=font_cn; fpb=font_cn_b; title='有限时间奇性所需的三种“逃逸”与 MESH8.0 封闭'; center='有限时间\n奇性包'; items=[('静默生成第三来源','违反：仅 D/I/K/W/P 有语义权\n缺失内容不得自动生成'),('抹去已登记来源差异','违反：I 差异必须保留并进入 K\n别名不得静默偷换'),('把潜在无界实例实体化为完成无穷','违反：任一实际有限时刻只实例化有限证书\n规则开放不等于对象内完成无穷')]; conclusion='三条逃逸路径均无合法核心路由，奇性不能成为完整语义输出。'
    else:
        fp=None; fpb=None; title='Three Escapes Required by a Finite-Time Singularity - and Their MESH8.0 Closure'; center='Finite-time\nsingularity packet'; items=[('Silently create a third source','Violates: only D/I/K/W/P have semantic authority\nmissing content is never auto-generated'),('Erase a registered provenance difference','Violates: I-differences must be preserved into K\nalias meaning cannot be silently substituted'),('Turn potentially unbounded instances into a completed infinity','Violates: every actual finite time instantiates a finite certificate\nopen rule reuse is not an infinity inside one object')]; conclusion='No escape has a legal core route; a singularity cannot become a complete semantic output.'
    ax.text(5,5.0,title,ha='center',fontsize=17.5,color=NAVY,fontproperties=fpb,weight='bold')
    box(ax,(4.0,2.05),2.0,1.25,center,fc='#FBECE9',ec=RED,fontsize=13,fp=fp,lw=2)
    coords=[(0.3,3.15),(7.0,3.15),(3.7,0.25)]
    for (head,desc),(x,y) in zip(items,coords):
        box(ax,(x,y),2.7,1.45,head+'\n'+desc,fc=CREAM if y>1 else LIGHT,ec=GOLD if y>1 else TEAL,fontsize=9.5,fp=fp)
        arrow(ax,(x+1.35,y+0.72),(5.0,2.68),RED,lw=1.6)
        ax.text((x+1.35+5.0)/2,(y+0.72+2.68)/2,'×',fontsize=18,color=RED,ha='center',va='center',fontproperties=fpb)
    ax.text(5,0.02,conclusion,ha='center',va='bottom',fontsize=11.5,color=TEAL,fontproperties=fpb)
    save(fig,f'fig3_singularity_{lang}.png')

# Figure 4: proof chain
for lang in ['cn','en']:
    fig,ax=plt.subplots(figsize=(12,4.8)); ax.set_xlim(0,12); ax.set_ylim(0,5); ax.axis('off')
    if lang=='cn':
        fp=font_cn; fpb=font_cn_b; title='三维 Navier–Stokes 非传统证明主链'; steps=['光滑不可压缩\n初始来源包','输运仅重排\n同一来源','差异进入 I\n完整登记','黏性消解\n极大未决差异','压力闭合\n不可压缩 K','光滑有限时刻\n正常形','对任意有限 T\n开放复用']; foot='有限对象 → 显式差异 → 内生消解 → 非再生 → 任意有限时刻可继续'
    else:
        fp=None; fpb=None; title='The Non-Traditional 3D Navier–Stokes Proof Chain'; steps=['Smooth divergence-free\ninitial provenance packet','Transport only rearranges\nthe same provenance','Differences enter I\nand are fully registered','Viscosity eliminates\nmaximal unresolved differences','Pressure closes\nincompressible K','Smooth finite-time\nnormal form','Open reuse for\nevery finite T']; foot='finite object → explicit difference → endogenous elimination → no regeneration → continuation at every finite time'
    ax.text(6,4.55,title,ha='center',fontsize=18,color=NAVY,fontproperties=fpb,weight='bold')
    xs=[0.15,1.85,3.55,5.25,6.95,8.65,10.35]
    for i,(x,txt) in enumerate(zip(xs,steps)):
        box(ax,(x,1.75),1.5,1.45,txt,fc=LIGHT if i%2==0 else '#EDF6F3',ec=TEAL if i in [2,3,4] else NAVY,fontsize=9.7,fp=fp)
        if i<len(steps)-1: arrow(ax,(x+1.5,2.47),(xs[i+1],2.47),GOLD,lw=1.7)
    ax.text(6,0.65,foot,ha='center',fontsize=11.2,color=TEAL,fontproperties=fpb)
    save(fig,f'fig4_chain_{lang}.png')

# Figure 5: status layers
for lang in ['cn','en']:
    fig,ax=plt.subplots(figsize=(9.5,5.4)); ax.set_xlim(0,10); ax.set_ylim(0,5.6); ax.axis('off')
    if lang=='cn':
        fp=font_cn; fpb=font_cn_b; title='三层成立状态：证明本体、保真编译与外部认证'; labels=[('语义证明本体','MESH8.0 内部\n同源输运—黏性消解闭环','本报告完成'),('经典保真编译','u、p、方程、光滑性、全局时间\n逐项对应','接口列出，待独立核验'),('外部认证','同行审阅、形式化与共同体确认','尚未完成')]
    else:
        fp=None; fpb=None; title='Three Status Layers: Proof Body, Fidelity Compilation, and External Certification'; labels=[('Semantic proof body','MESH8.0 internal\nco-provenance transport-viscosity closure','completed in this report'),('Classical fidelity compilation','u, p, equations, smoothness, and global time\nmapped interface by interface','interfaces stated; independent verification pending'),('External certification','peer review, formalization, and community confirmation','not completed')]
    ax.text(5,5.1,title,ha='center',fontsize=17.5,color=NAVY,fontproperties=fpb,weight='bold')
    ys=[3.55,2.05,0.55]; colors=[('#EDF6F3',TEAL),(LIGHT,NAVY),(CREAM,GOLD)]
    for (head,desc,status),(y,(fc,ec)) in zip(labels,zip(ys,colors)):
        box(ax,(0.8,y),2.3,1.05,head,fc=fc,ec=ec,fontsize=12,fp=fp)
        box(ax,(3.35,y),3.9,1.05,desc,fc='white',ec=GREY,fontsize=10.7,fp=fp)
        box(ax,(7.5,y),1.7,1.05,status,fc=fc,ec=ec,fontsize=10.5,fp=fp)
        arrow(ax,(3.1,y+0.52),(3.35,y+0.52),GREY,lw=1.2)
        arrow(ax,(7.25,y+0.52),(7.5,y+0.52),GREY,lw=1.2)
    save(fig,f'fig5_status_{lang}.png')

print('created', len(list(OUT.glob('*.png'))), 'figures')
