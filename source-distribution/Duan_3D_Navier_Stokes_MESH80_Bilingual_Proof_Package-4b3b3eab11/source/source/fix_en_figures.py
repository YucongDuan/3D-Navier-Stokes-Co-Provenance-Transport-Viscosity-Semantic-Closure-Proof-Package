from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT=Path('/mnt/data/navier_mesh80_work/figures')
NAVY='#173A5E'; TEAL='#2B7A78'; GOLD='#C58F2B'; LIGHT='#EAF3F5'; CREAM='#FBF4E6'; GREY='#6B7C8C'; GREEN='#4D7C5A'; WHITE='#FFFFFF'

def save(fig,name):
    fig.savefig(OUT/name, dpi=260, bbox_inches='tight', facecolor='white')
    plt.close(fig)

def box(ax,x,y,w,h,text,fc=LIGHT,ec=NAVY,fontsize=9.0,lw=1.6):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=0.025',facecolor=fc,edgecolor=ec,linewidth=lw)
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fontsize,color=NAVY,linespacing=1.08)
    return p

def arrow(ax,start,end,color=GREY,lw=1.4):
    a=FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=14,linewidth=lw,color=color)
    ax.add_patch(a)
    return a

# Figure 2 - three roles, enlarged and rewrapped
fig,ax=plt.subplots(figsize=(12.8,6.0)); ax.set_xlim(0,12.8); ax.set_ylim(0,6.0); ax.axis('off')
ax.text(6.4,5.62,'Three Roles Inside One Fluid Provenance:\nTransport, Viscosity, and Pressure',ha='center',va='center',fontsize=17.0,color=NAVY,weight='bold',linespacing=1.0)
box(ax,0.35,2.30,2.35,1.28,'Single momentum packet\nD: one fluid identity',fc=CREAM,ec=GOLD,fontsize=10.2)
role_x=3.35; role_w=2.8; role_h=1.18
role_data=[
    (4.05,'Transport\nrelocates provenance\nno independent source',LIGHT,TEAL),
    (2.48,'Viscosity\neliminates registered differences\nonly included relations remain','#EDF6F3',GREEN),
    (0.91,'Pressure\ncloses incompressibility\nnot a third source','#EEF1F8',NAVY),
]
for y,txt,fc,ec in role_data:
    box(ax,role_x,y,role_w,role_h,txt,fc=fc,ec=ec,fontsize=8.7)
out_x=8.25; out_w=3.65; out_y=2.15; out_h=1.58
box(ax,out_x,out_y,out_w,out_h,'Smooth finite-time normal form\nP: complete, continuable output',fc='#F2F7F6',ec=TEAL,fontsize=10.0)
for y,_,_,_ in role_data:
    cy=y+role_h/2
    arrow(ax,(2.70,2.94),(role_x,cy))
    arrow(ax,(role_x+role_w,cy),(out_x,out_y+out_h/2))
ax.text(6.4,0.18,'The three roles are explicit core routes inside one provenance packet, not three independent ontological poles.',ha='center',va='bottom',fontsize=9.7,color=GREY)
save(fig,'fig2_roles_en.png')

# Figure 4 - proof chain with smaller text and more box width
fig,ax=plt.subplots(figsize=(14.5,4.9)); ax.set_xlim(0,14.5); ax.set_ylim(0,4.9); ax.axis('off')
ax.text(7.25,4.52,'The Non-Traditional 3D Navier-Stokes Proof Chain',ha='center',fontsize=18.0,color=NAVY,weight='bold')
steps=[
    'Smooth divergence-free\ninitial provenance\npacket',
    'Transport rearranges\nthe same\nprovenance',
    'Differences enter I\nand are explicitly\nregistered',
    'Viscosity eliminates\nmaximal unresolved\ndifferences',
    'Pressure closes\nincompressible\nK',
    'Smooth finite-time\nnormal\nform',
    'Open reuse for\nevery finite\nT',
]
box_w=1.72; gap=0.28; start=0.18; y=1.78; h=1.55
xs=[start+i*(box_w+gap) for i in range(7)]
for i,(x,txt) in enumerate(zip(xs,steps)):
    box(ax,x,y,box_w,h,txt,fc=LIGHT if i%2==0 else '#EDF6F3',ec=TEAL if i in [2,3,4] else NAVY,fontsize=7.6)
    if i<6:
        arrow(ax,(x+box_w,y+h/2),(xs[i+1],y+h/2),color=GOLD,lw=1.7)
ax.text(7.25,0.62,'finite object  →  explicit difference  →  endogenous elimination  →  no regeneration  →  continuation at every finite time',ha='center',fontsize=10.2,color=TEAL,weight='bold')
save(fig,'fig4_chain_en.png')

# Figure 5 - status layers with non-overlapping text
fig,ax=plt.subplots(figsize=(12.5,6.4)); ax.set_xlim(0,12.5); ax.set_ylim(0,6.4); ax.axis('off')
ax.text(6.25,6.0,'Three Status Layers:\nProof Body, Fidelity Compilation, and External Certification',ha='center',va='center',fontsize=17.0,color=NAVY,weight='bold',linespacing=1.0)
rows=[
    ('Semantic proof body','MESH8.0 internal\nco-provenance transport-viscosity\nsemantic closure','Completed\nin this report','#EDF6F3',TEAL),
    ('Classical fidelity\ncompilation','u, p, equations, smoothness,\nand global time mapped\ninterface by interface','Interfaces stated;\nindependent verification\npending',LIGHT,NAVY),
    ('External\ncertification','Peer review, formalization,\nand community confirmation','Not\ncompleted',CREAM,GOLD),
]
ys=[4.15,2.42,0.69]
for (head,desc,status,fc,ec),y in zip(rows,ys):
    box(ax,0.35,y,2.25,1.22,head,fc=fc,ec=ec,fontsize=9.5)
    box(ax,2.95,y,5.05,1.22,desc,fc=WHITE,ec=GREY,fontsize=8.8)
    box(ax,8.35,y,3.40,1.22,status,fc=fc,ec=ec,fontsize=8.8)
    arrow(ax,(2.60,y+0.61),(2.95,y+0.61),color=GREY,lw=1.2)
    arrow(ax,(8.00,y+0.61),(8.35,y+0.61),color=GREY,lw=1.2)
save(fig,'fig5_status_en.png')
print('English figures regenerated')
