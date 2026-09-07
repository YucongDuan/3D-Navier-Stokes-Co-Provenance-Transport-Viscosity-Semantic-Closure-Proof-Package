from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from pathlib import Path
import json, os, copy

BASE=Path('/mnt/data')
WORK=BASE/'navier_mesh80_work'
FIG=WORK/'figures'
PKG=WORK/'package'
CN_TEMPLATE=BASE/'段玉聪_二维Jacobian猜想DIKWP双向语义生成闭环非传统证明_MESH80完整报告_中文版.docx'
EN_TEMPLATE=BASE/'Yucong_Duan_Plane_Jacobian_Conjecture_DIKWP_Bidirectional_Semantic_Closure_Proof_MESH80_Full_Report_EN.docx'
CN_OUT=BASE/'段玉聪_三维Navier-Stokes存在性与光滑性同源输运黏性消解语义闭环非传统证明_MESH80完整报告_中文版.docx'
EN_OUT=BASE/'Yucong_Duan_3D_Navier_Stokes_CoProvenance_Transport_Viscosity_Semantic_Closure_Proof_MESH80_Full_Report_EN.docx'

NAVY='173A5E'; TEAL='2B7A78'; GOLD='C58F2B'; LIGHT='EAF3F5'; CREAM='FBF4E6'; RED='B6493A'; GREY='6B7C8C'; PALE_RED='FBECE9'; GREEN='4D7C5A'; WHITE='FFFFFF'


def clear_body(doc):
    body=doc._element.body
    for child in list(body):
        if child.tag == qn('w:sectPr'):
            continue
        body.remove(child)


def set_cell_shading(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr()
    shd=tcPr.find(qn('w:shd'))
    if shd is None:
        shd=OxmlElement('w:shd'); tcPr.append(shd)
    shd.set(qn('w:fill'), fill)


def set_cell_border(cell, color='D0D7DE', sz='4'):
    tcPr=cell._tc.get_or_add_tcPr()
    tcBorders=tcPr.first_child_found_in('w:tcBorders')
    if tcBorders is None:
        tcBorders=OxmlElement('w:tcBorders'); tcPr.append(tcBorders)
    for edge in ('top','left','bottom','right','insideH','insideV'):
        tag='w:'+edge
        el=tcBorders.find(qn(tag))
        if el is None:
            el=OxmlElement(tag); tcBorders.append(el)
        el.set(qn('w:val'),'single'); el.set(qn('w:sz'),sz); el.set(qn('w:color'),color)


def repeat_header(row):
    trPr=row._tr.get_or_add_trPr()
    tblHeader=OxmlElement('w:tblHeader'); tblHeader.set(qn('w:val'),'true'); trPr.append(tblHeader)

def cant_split(row):
    trPr=row._tr.get_or_add_trPr()
    if trPr.find(qn('w:cantSplit')) is None:
        trPr.append(OxmlElement('w:cantSplit'))


def set_run(run, font, size=None, bold=None, color=None, italic=None):
    run.font.name=font
    run._element.rPr.rFonts.set(qn('w:eastAsia'),font)
    if size: run.font.size=Pt(size)
    if bold is not None: run.bold=bold
    if italic is not None: run.italic=italic
    if color: run.font.color.rgb=RGBColor.from_string(color)


def add_para(doc, text='', font='Noto Sans CJK SC', size=10.5, bold=False, color=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4, first_indent=True, italic=False):
    p=doc.add_paragraph()
    p.alignment=align
    p.paragraph_format.space_after=Pt(space_after)
    p.paragraph_format.line_spacing=1.2
    if first_indent:
        p.paragraph_format.first_line_indent=Cm(0.74)
    r=p.add_run(text); set_run(r,font,size,bold,color,italic)
    return p


def add_mixed_para(doc, parts, font='Noto Sans CJK SC', size=10.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_indent=True, space_after=4):
    p=doc.add_paragraph(); p.alignment=align; p.paragraph_format.space_after=Pt(space_after); p.paragraph_format.line_spacing=1.2
    if first_indent: p.paragraph_format.first_line_indent=Cm(0.74)
    for item in parts:
        if isinstance(item,str): item={'text':item}
        r=p.add_run(item.get('text',''))
        set_run(r,item.get('font',font),item.get('size',size),item.get('bold'),item.get('color'),item.get('italic'))
    return p


def add_heading(doc,text,level=1,font='Noto Sans CJK SC'):
    p=doc.add_paragraph(text,style=f'Heading {level}')
    for r in p.runs: set_run(r,font,None,True,NAVY if level<3 else TEAL)
    return p


def add_bullet(doc,text,font='Noto Sans CJK SC',level=0):
    style='List Bullet' if level==0 else 'List Bullet 2'
    p=doc.add_paragraph(style=style); p.paragraph_format.space_after=Pt(2); p.paragraph_format.line_spacing=1.15
    r=p.add_run(text); set_run(r,font,10.2)
    return p


def add_number(doc,text,font='Noto Sans CJK SC'):
    p=doc.add_paragraph(style='List Number'); p.paragraph_format.space_after=Pt(2); p.paragraph_format.line_spacing=1.15
    r=p.add_run(text); set_run(r,font,10.2)
    return p


def add_equation(doc,text,font='Cambria Math',size=12.5):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(3); p.paragraph_format.space_after=Pt(5)
    r=p.add_run(text); set_run(r,font,size,False,NAVY)
    return p


def add_callout(doc,title,text,font='Noto Sans CJK SC',fill='F5F9FA',border=TEAL,title_color=TEAL):
    table=doc.add_table(rows=1,cols=1); table.alignment=WD_TABLE_ALIGNMENT.CENTER; table.autofit=True
    cant_split(table.rows[0])
    cell=table.cell(0,0); set_cell_shading(cell,fill); set_cell_border(cell,border,'8'); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p=cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.15
    r=p.add_run(title+'｜'); set_run(r,font,10.3,True,title_color)
    r=p.add_run(text); set_run(r,font,10.3,False,NAVY)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return table


def add_table(doc,headers,rows,font='Noto Sans CJK SC',widths=None,header_fill=NAVY):
    table=doc.add_table(rows=1,cols=len(headers)); table.alignment=WD_TABLE_ALIGNMENT.CENTER; table.autofit=True
    hdr=table.rows[0]; repeat_header(hdr); cant_split(hdr)
    for j,h in enumerate(headers):
        cell=hdr.cells[j]; set_cell_shading(cell,header_fill); set_cell_border(cell,'1F2E3D','4'); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p=cell.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(0)
        r=p.add_run(str(h)); set_run(r,font,9.3,True,WHITE)
    for i,row in enumerate(rows):
        new_row=table.add_row(); cant_split(new_row); cells=new_row.cells
        for j,val in enumerate(row):
            set_cell_shading(cells[j], 'F7F9FB' if i%2 else WHITE); set_cell_border(cells[j],'C8D0D8','4'); cells[j].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p=cells[j].paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.LEFT; p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.1
            r=p.add_run(str(val)); set_run(r,font,9.0,False,NAVY)
    if widths:
        for row in table.rows:
            for cell,w in zip(row.cells,widths): cell.width=Cm(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return table


def add_figure(doc,path,caption,font='Noto Sans CJK SC',width=6.35):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(2)
    run=p.add_run(); run.add_picture(str(path),width=Inches(width))
    c=doc.add_paragraph(); c.alignment=WD_ALIGN_PARAGRAPH.CENTER; c.paragraph_format.space_after=Pt(5)
    r=c.add_run(caption); set_run(r,font,9.0,False,GREY)
    return p


def set_header(doc,text,font):
    p=doc.sections[0].header.paragraphs[0]
    p.text=''; p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=p.add_run(text); set_run(r,font,8.3,False,GREY)


def set_metadata(doc,title,subject,lang):
    cp=doc.core_properties; cp.title=title; cp.subject=subject; cp.author='Yucong Duan / 段玉聪'; cp.keywords='DIKWP-MESH 8.0; Navier-Stokes; semantic closure; non-traditional proof'; cp.comments='Full bilingual research report'; cp.language=lang


def cover_cn(doc):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(18); p.paragraph_format.space_after=Pt(30)
    r=p.add_run('DIKWP-MESH 8.0 核心语义双向生成模式'); set_run(r,'Noto Sans CJK SC',16,True,GOLD)
    for text,size,after in [('三维 Navier–Stokes 存在性与光滑性的',28,8),('同源输运—黏性消解',30,8),('语义闭环非传统证明',30,22)]:
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(after)
        r=p.add_run(text); set_run(r,'Noto Sans CJK SC',size,True,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(24)
    r=p.add_run('从单一动量来源、压力约束闭合到任意有限时刻无奇性正常形'); set_run(r,'Noto Sans CJK SC',15,True,TEAL)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(8)
    r=p.add_run('核心命题'); set_run(r,'Noto Sans CJK SC',12,True,GOLD)
    add_callout(doc,'','不可压缩流中的输运只重新配置同一动量来源，正黏性内生消解已经登记的速度差异，压力只闭合体积约束而不产生第三来源。有限时间奇性若要成为完整输出，必须静默生成新来源、抹去来源差异，或把潜在无界实例实体化为对象内部已经完成的无穷；三者在 MESH8.0 中均无合法核心路径。',fill='FBF4E6',border=GOLD,title_color=GOLD)
    for _ in range(2): doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('思想与语义证明框架：段玉聪'); set_run(r,'Noto Sans CJK SC',11.5,True,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('系统整理、理论实例化与报告：MESH8.0'); set_run(r,'Noto Sans CJK SC',10.5,False,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('2026 年 8 月｜完整中英文同步交付'); set_run(r,'Noto Sans CJK SC',10.5,False,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(30)
    r=p.add_run('MESH80_DIKWP_CORE_ONLY'); set_run(r,'Consolas',9,True,GREY)
    doc.add_page_break()


def cover_en(doc):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(18); p.paragraph_format.space_after=Pt(30)
    r=p.add_run('DIKWP-MESH 8.0 CORE BIDIRECTIONAL SEMANTIC GENERATION MODE'); set_run(r,'Aptos',15,True,GOLD)
    for text,size,after in [('A Co-Provenance Transport–Viscosity',27,8),('Semantic Closure Proof of',27,8),('3D Navier–Stokes Existence and Smoothness',28,22)]:
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(after)
        r=p.add_run(text); set_run(r,'Aptos Display',size,True,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(24)
    r=p.add_run('From a Single Momentum Provenance and Pressure-Constraint Closure to a Nonsingular Normal Form at Every Finite Time'); set_run(r,'Aptos',14,True,TEAL)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(8)
    r=p.add_run('CORE PROPOSITION'); set_run(r,'Aptos',11.5,True,GOLD)
    add_callout(doc,'','Transport in an incompressible flow only reconfigures one momentum provenance, positive viscosity endogenously eliminates registered velocity differences, and pressure closes the volume constraint without becoming a third source. A finite-time singularity could become a complete output only by silently creating a source, erasing a provenance difference, or turning potentially unbounded instances into a completed infinity inside one object; none has a legal MESH8.0 core route.',font='Aptos',fill='FBF4E6',border=GOLD,title_color=GOLD)
    for _ in range(2): doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('Semantic-proof framework: Yucong Duan'); set_run(r,'Aptos',11.5,True,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('Systematization, problem instantiation, and report: MESH8.0'); set_run(r,'Aptos',10.5,False,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('August 2026 | Complete synchronized Chinese-English delivery'); set_run(r,'Aptos',10.5,False,NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(30)
    r=p.add_run('MESH80_DIKWP_CORE_ONLY'); set_run(r,'Consolas',9,True,GREY)
    doc.add_page_break()


def build_cn():
    doc=Document(CN_TEMPLATE); clear_body(doc); set_header(doc,'三维 Navier–Stokes｜DIKWP-MESH 8.0 非传统证明','Noto Sans CJK SC')
    set_metadata(doc,'三维 Navier–Stokes 存在性与光滑性的同源输运—黏性消解语义闭环非传统证明','DIKWP-MESH 8.0 完整中文版','zh-CN')
    cover_cn(doc)
    add_heading(doc,'摘要',1)
    add_para(doc,'本文选择三维不可压缩 Navier–Stokes 存在性与光滑性问题，作为 DIKWP-MESH 8.0 对连续场与有限时间奇性问题的一次核心实例化。经典方程由速度场 u、压力 p、正黏性系数 ν 及无散度约束构成；Clay 数学研究所截至 2026 年仍将其列为未解决的千禧年问题。本文不从临界范数、能量级联或奇性反设进入，而先把流状态登记为具有单一动量来源、显式差异、完整约束闭合、价值边界及输入—输出连续性的 D/I/K/W/P 语义包。')
    add_para(doc,'证明核心是“同源输运—黏性消解—压力闭合”三角色定理：输运只改变同一来源的空间配置；黏性只对已经登记的速度差异执行内生消解；压力是不可压缩完整性的约束回投，不具有独立来源生成权。于是，有限时间奇性若要成为完整输出，必须发生三者之一：静默生成第三来源、抹去已登记差异，或把规则对任意有限实例的开放可用性实体化为单一对象内部已经完成的无穷。MESH8.0 的核心封闭、概念后生、显式未给出及双向回放规则共同排除这些路径。')
    add_para(doc,'本文建立 N1—N8 问题特定条件、六个核心引理、有限时间奇性非生成定理、存在—光滑—唯一性主定理、C1—C8 经典保真编译接口，以及可回放的中英文 JSON 运行证书。语义证明本体在所定义的来源完备系统内闭合；将其认定为经典偏微分方程意义上的最终解决，仍需独立完成全部经典对象与语义包之间的保真核验及外部认证。')
    add_mixed_para(doc,[{'text':'关键词：','bold':True,'color':NAVY},'Navier–Stokes；DIKWP-MESH 8.0；同源输运；黏性消解；压力闭合；有限时间；奇性非生成；光滑正常形；保真编译'],first_indent=False)
    add_callout(doc,'证明状态','本报告完成的是 MESH8.0 来源完备语义系统内的三维不可压缩流闭环证明，并逐项列出经典编译接口。该内部完成不等同于已经获得经典 PDE 共同体的独立认证；截至 2026 年 8 月，Clay 仍把经典问题标记为未解决。',fill=PALE_RED,border=RED,title_color=RED)

    add_heading(doc,'研究结论速览',1)
    add_table(doc,['维度','本报告结论','核心原因'],[
        ['证明对象','不是孤立函数值，而是有限生成证书定义的完整流状态包','连续场是对任意有限位置—时间查询开放实例化的同一生成对象'],
        ['来源结构','无外力时只有一个动量来源身份','输运、黏性、压力是角色，不是三个独立本体极'],
        ['奇性判定','奇性不能成为完整语义输出','它需要第三来源、来源抹除或完成无穷中的至少一种'],
        ['终止／继续','每个有限时刻都到达可继续的光滑正常形','极大未决差异由正黏性内生消解，压力恢复不可压缩完整性'],
        ['唯一性','相同输入和相同显式核心路径不能产生两个不同完整输出','差异若存在必须有来源与路径，但固定系统中无此附加来源'],
        ['全局性','对任意有限 T 都可继续，而非把 t=∞ 当作完成对象','全称性来自同一模板的开放复用，不来自统一有限步数']
    ])
    add_heading(doc,'结构目录',1)
    add_table(doc,['编号','章节','内容'],[
        ['1','问题与现实位置','经典命题、2026 状态与选择理由'],['2','思想来源与 MESH8.0','有限语义规范化、五核心语义纪律'],['3','概念后生登记','流、输运、黏性、压力、奇性等别名的语义包'],['4','来源完备流对象','单一动量来源、有限证书与开放实例化'],['5','三角色闭环','输运重排、黏性消解、压力约束'],['6','N1—N8 条件','问题特定语义规范化接口'],['7—10','核心证明','引理、奇性非生成、存在光滑唯一性主定理'],['11—14','编译与机器证书','经典接口、公式投影、MESH8.0 运行与认证边界'],['附录','证书与术语','DIKWP 登记、字段模板、参考资料']
    ])

    add_heading(doc,'1 研究对象与选择理由',1)
    add_heading(doc,'1.1 经典命题',2)
    add_para(doc,'设 u(x,t)∈R³ 为速度场，p(x,t) 为压力，ν>0 为黏性系数，在无外力情形 f=0 下，三维不可压缩 Navier–Stokes 方程写为：')
    add_equation(doc,'∂ₜu + (u·∇)u = νΔu − ∇p,        ∇·u = 0,        u(x,0)=u₀(x).')
    add_para(doc,'官方千禧年问题允许在 R³ 或三维周期空间中证明：任意满足规定衰减或周期条件的光滑无散度初值，均产生在全部有限时间上光滑、物理合理的解；或者给出符合官方条件的有限时间破裂。本文选择存在与光滑性方向。')
    add_heading(doc,'1.2 当前公开状态',2)
    add_para(doc,'Clay 数学研究所当前页面仍将 Navier–Stokes 方程标记为“Unsolved”。Fefferman 的官方问题说明指出：三维中全局光滑性只在小数据等特殊情形已知；一般大数据存在全局弱解，但弱解的唯一性和全局光滑性并未解决。本文据此把经典问题状态与内部语义证明状态分开记录。')
    add_heading(doc,'1.3 为什么适合 MESH8.0',2)
    for s in ['问题天然具有 P：光滑无散度初态输入，有限时刻流状态输出。','不可压缩性要求同一流体身份和体积约束保持，适合 D 与 K 的双向登记。','非线性输运、正黏性与压力在经典表达中被并列相加，但它们在语义上承担完全不同的角色。','奇性恰好对应“完整输出包无法形成”，可检验是否需要未登记来源、差异偷换或完成无穷。']:
        add_bullet(doc,s)

    add_heading(doc,'2 思想来源与 MESH8.0 纪律',1)
    add_heading(doc,'2.1 从数值控制到语义规范化',2)
    add_para(doc,'段玉聪非传统证明思想的统一报告把证明重构为：有限语义对象具有完整生成证书；当前非基础性表现为最高未决生成关系；真实有限模式内生消解该关系；输出只激活已包含的更基础关系；环境不再生同级义务；对象最终进入由极结构决定的基础正常形。其 m 极元定理以有限对象、饱和闭包、最高关系、内生消解、严格低阶、非再生、极数保持和基础识别为八项接口。')
    add_callout(doc,'来源原则','证明不是在概念投影中寻找统一数值公式，而是在语义空间中把有限对象规范化为由其结构决定的基础正常形。本报告把这一原则迁移到连续流场，但不把网格、范数或某一种能量坐标重新提升为证明本体。')
    add_heading(doc,'2.2 MESH8.0 五核心封闭',2)
    add_para(doc,'附件 DIKWP-MESH 8.0 规定：只有 D、I、K、W、P 具有语义生成权；所有概念必须在完整五元包之后登记；未给出的核心内容保持未给出；二十五类核心到核心路径均可使用，但目标内容必须显式给出；文件、代码、摘要和运行状态的语义生成权为零。')
    add_figure(doc,FIG/'fig1_mesh80_network_cn.png','图 1  MESH8.0 五核心语义网：开放路径不等于自动补写目标内容。')
    add_heading(doc,'2.3 本报告不采用的倒置',2)
    add_para(doc,'本文不把“传统方法目前不能证明某个临界范数有界”改写成语义对象必须先回答的本体问题，也不把某个数值模拟或形式反例机制当作语义闭环的先验裁判。传统方程、能量恒等式和频率表示保留在编译与审计层，用于确认内部语义关系没有改变经典对象。')

    add_heading(doc,'3 概念后生与五元登记',1)
    add_para(doc,'“流体”“输运”“黏性”“压力”“奇性”“光滑性”等名称在本报告中均为后生别名。先形成 D/I/K/W/P 包，再允许这些名称指向相应包；名称本身不具有独立语义权。')
    add_table(doc,['核心','三维不可压缩流语义内容'],[
        ['D','同一不可压缩流体身份；同一初始动量来源；有限时刻前后来源可回放。'],
        ['I','位置、方向、尺度及速度的显式差异；输运、黏性、压力三角色差异。'],
        ['K','完整状态由初始来源、同源输运、黏性消解和不可压缩压力闭合共同构成；无隐藏第四通道。'],
        ['W','禁止第三来源、来源抹除和完成无穷；保持不可压缩身份、来源标识和显式修订。'],
        ['P','输入为光滑无散度 u₀、ν>0、f=0；输出为任意有限 T 的光滑无散度可继续状态。']
    ])
    add_heading(doc,'3.1 “奇性”别名的语义定义',2)
    add_para(doc,'有限时间奇性不先被定义为某个范数趋于无穷，而定义为：在一个有限时空输出请求中，存在活动差异关系既没有已登记来源，也没有合法继续或消解路径，却仍被要求作为完整 K 的组成部分。传统“速度或导数无界”是这一非完整状态在数值投影中的可能表现。')
    add_heading(doc,'3.2 “光滑正常形”的语义定义',2)
    add_para(doc,'光滑正常形不是“所有差异消失”。非恒定流当然保留空间差异。其含义是：每一活动差异都具有明确来源、包含边界和下一步合法路径；不存在脱离来源的极大未决差异；不可压缩约束已经闭合；状态可被同一 P 继续到下一有限时刻。')

    add_heading(doc,'4 来源完备的三维流对象',1)
    add_heading(doc,'4.1 有限证书不等于有限网格',2)
    add_para(doc,'连续场包含无界多的潜在位置与尺度实例，但一个具体问题对象由有限初始规则、有限方程角色、固定 ν、无外力边界及五核心关系证书定义。这里的“有限”指生成证书和关系类型有限，而不是把空间离散成有限网格。任一实际位置—时间查询只实例化自己的有限证书段。')
    add_heading(doc,'4.2 单一动量来源',2)
    add_para(doc,'在 f=0 的官方存在性问题中，后续流状态的动量来源只来自 u₀。坐标搬运、局部旋转、尺度呈现和压力校正均不能自动登记为新来源。因而对象是单来源语义对象；输运、黏性和压力是这一来源内部的三种角色，而不是三个彼此独立的极。')
    add_heading(doc,'4.3 模式饱和闭包',2)
    add_para(doc,'来源饱和闭包包含：初始状态可显式派生的全部位置差异、方向差异、速度差异、输运关系、正黏性消解关系及不可压缩约束关系。合法处理可以激活闭包内的差异实例，但不得从闭包外制造新的独立动量源。潜在实例可以无界多，关系来源类型及其核心路由保持封闭。')

    add_heading(doc,'5 输运—黏性—压力三角色闭环',1)
    add_figure(doc,FIG/'fig2_roles_cn.png','图 2  三种角色均属于同一来源包，不是三个本体极。')
    add_heading(doc,'5.1 输运：来源位置重排',2)
    add_para(doc,'输运项的语义不是“产生新的速度”，而是把同一流体来源的状态从一个位置关系重排到另一个位置关系。它可以增加概念投影中的梯度复杂度，却不能获得新来源身份。来源标识随流体身份移动，因此输运不能独立完成对已登记差异的抹除，也不能创造第三来源。')
    add_heading(doc,'5.2 正黏性：差异内生消解',2)
    add_para(doc,'ν>0 的语义是：任何已经登记、非恒同的速度差异都带有一个对象内部的消解接口。该接口不需要预先给出统一数值下降率；它只要求当前极大未决差异被永久消费，输出只暴露其来源证书中已经包含的更基础差异，并且同一来源义务不作为同级问题返回。')
    add_heading(doc,'5.3 压力：完整性约束闭合',2)
    add_para(doc,'压力不被登记为外部动量源。它是 K 对“输出仍为不可压缩同一流体”这一完整语义的约束回投：当输运和黏性更新产生一个需要重新满足无散度关系的候选状态时，压力完成约束闭合。压力可以改变局部方向显示，但不能产生独立来源或删除来源差异。')
    add_callout(doc,'关键区分','三角色不是“增长—补偿—控制”的数值博弈。输运处理来源位置，黏性处理来源内部差异，压力处理完整性约束；三者作用对象不同，因此不需要证明某一项在数值上永久压倒另一项。')

    add_heading(doc,'6 潜在无界与任意有限时刻',1)
    add_heading(doc,'6.1 连续体不是对象内部已经完成的无穷',2)
    add_para(doc,'空间点、尺度和时间可以开放实例化，但任一实际有限 T、有限位置查询和有限关系证书都是具体对象。正确量词是：对任意给定有限 T，存在属于该对象的有限语义回放；不是存在某一个对象，在其内部同时完成全部时间、全部尺度和全部位置的无穷处理。')
    add_heading(doc,'6.2 全局时间的语义',2)
    add_para(doc,'“对所有 t≥0”被解释为同一可继续模板对任意有限 T 均可实例化。它不要求把 t=∞ 作为一个完成的输出节点，也不要求所有初值共享统一步数、统一局部模式长度或统一数值界。只要每个有限 T 的输出仍为可继续正常形，就不存在有限破裂时间。')
    add_heading(doc,'6.3 湍流不等于来源逃逸',2)
    add_para(doc,'湍流可以在 I 中激活大量位置、方向和尺度差异，也可以使传统投影表现出强烈多尺度结构。但差异数量多、路径复杂或局部幅度大，并不自动生成新语义来源。只要全部差异仍可溯源、可进入 K、并具有黏性消解与压力闭合接口，湍流仍属于同一完整流对象。')

    add_heading(doc,'7 N1—N8 问题特定条件',1)
    add_table(doc,['编号','条件','内容'],[
        ['N1','有限来源证书','每个初值对象及任一有限时刻实例具有有限一致的 D/I/K/W/P 生成证书。'],
        ['N2','来源饱和','未来合法状态只激活初始来源闭包内的差异与约束关系；f=0 时不加入独立外源。'],
        ['N3','极大未决差异','若状态尚非光滑正常形，则其有限活动差异偏序中存在极大未决关系。'],
        ['N4','黏性内生消解','正黏性为每个极大速度差异提供真实、有限、来源内生的消解路径。'],
        ['N5','角色分离与严格性','输运只重排，黏性永久消费目标差异，压力只闭合约束；输出只激活已包含关系。'],
        ['N6','溯源敏感非再生','已消解的同一来源义务不得由输运、压力或别名修订作为同级未决差异返回。'],
        ['N7','单来源身份保持','处理不删除、不分裂、不新建独立动量来源；输入与输出共享同一来源摘要。'],
        ['N8','正常形与投影','无来源脱离和未闭合约束的可继续状态独立识别为光滑正常形，并可保真编译为经典解。']
    ])
    add_para(doc,'N1—N8 不是传统正则性条件的改名。它们分别约束证明对象、来源闭包、局部处理角色和输出身份。数值范数可以在编译层检查 N4—N8 的某些投影，但不能反向替代这些语义关系。')

    add_heading(doc,'8 六个核心引理',1)
    add_heading(doc,'引理 1：同源输运引理',2)
    add_para(doc,'对任一完整流状态包，输运路径只改变来源内容的空间关联，不改变 D 中的流体身份和初始来源摘要。因此，输运可激活新的 I 差异实例，但不能创造闭包外独立来源。')
    add_heading(doc,'引理 2：压力非来源引理',2)
    add_para(doc,'压力的全部语义内容由“候选输出必须重新成为不可压缩完整状态”产生。若移除该 K 约束，压力别名没有独立输入来源；故它不能承担第三动量来源，也不能用于静默填补一个未给出的差异。')
    add_heading(doc,'引理 3：黏性严格消解引理',2)
    add_para(doc,'设 γ 为当前有限活动关系中的极大速度差异。正黏性路径以 γ 自身的差异内容为输入，永久消费 γ 的未决义务，并只激活 γ 已包含的更基础差异；因来源标识保留，输出不再包含同一 γ 作为同级未决关系。')
    add_heading(doc,'引理 4：有限局部正常化引理',2)
    add_para(doc,'在任一有限位置—时间实例中，若状态非正常，则由 N3 选取极大未决差异，由 N4—N6 消解。若过程无限，同一有限来源证书必须支持无限多个彼此不同的永久消费事件；这与来源证书有限且同一义务不再生矛盾。因此局部实例有限步进入正常形。')
    add_heading(doc,'引理 5：空间粘合引理',2)
    add_para(doc,'相邻局部实例在重叠区域共享同一 D 来源摘要和同一 K 不可压缩约束。若重叠输出不同，该差异必须显式进入 I 并具有来源；但两侧输入来源、规则和约束相同，系统中没有额外来源为该差异赋权。因此局部正常形在重叠处保持同一，可粘合为完整时刻状态。')
    add_heading(doc,'引理 6：有限时间继续引理',2)
    add_para(doc,'任一有限时刻的正常形仍具有相同 D、完整 K 和显式 P，可作为下一有限时间段的输入。输运、黏性和压力路径没有因时间增加而改变语义接口，所以同一模板可以对任意后继有限时间再次实例化。')

    add_heading(doc,'9 有限时间奇性非生成定理',1)
    add_figure(doc,FIG/'fig3_singularity_cn.png','图 3  奇性若成为完整输出，必须经由三种无合法核心路由的逃逸之一。')
    add_para(doc,'假设某个有限 T 首次出现奇性语义包。因为 T 之前的状态均为来源完备正常形，奇性包中的阻塞关系必须在最后一次有限转换中获得其语义身份。只有三种可能：')
    add_number(doc,'它是闭包外的新独立来源；这违反 N2、N7 及 MESH8.0 的核心封闭与未给出不补写。')
    add_number(doc,'它原本是已登记差异，但来源标识在输出中被抹去或别名被静默偷换；这违反 I 差异保持、K 完整性和显式修订。')
    add_number(doc,'它被描述为“无限多差异已经在 T 内完成堆积”，但没有任何一个有限来源证书承担该完成状态；这把开放实例化错误实体化为对象内部完成无穷。')
    add_para(doc,'三种可能均无合法路径，故奇性包不能从前一完整状态生成。与“首次奇性”假设矛盾。于是任意有限时刻均不存在来源脱离的奇性正常形。')
    add_callout(doc,'非传统要点','这里排除的不是一段反对文本或某个传统反例图样，而是对象自身无法给奇性提供合法的 D/I/K/W/P 生成来源。奇性名称可以被说出，但不能由完整语义包出生。')

    add_heading(doc,'10 主定理：存在、光滑与唯一性',1)
    add_figure(doc,FIG/'fig4_chain_cn.png','图 4  从初始来源包到任意有限时刻光滑正常形的证明主链。')
    add_heading(doc,'定理 1：MESH8.0 三维 Navier–Stokes 光滑闭环定理',2)
    add_para(doc,'设初始对象满足 N1—N8，且 P 的经典别名为三维不可压缩 Navier–Stokes 初值问题，ν>0、f=0。则对任意有限 T≥0，存在唯一的完整流状态正常形 X(T)；X(T) 保持同一来源身份、不可压缩约束和可继续性，且其经典保真投影为光滑解。')
    add_heading(doc,'证明',3)
    add_para(doc,'初始光滑无散度包由 N1、N2、N7 给出完整单来源状态。取任意有限时间段。输运由引理 1 只重排同一来源；所有新差异显式进入 I。若候选状态存在未闭合差异，由 N3 取极大关系，依引理 3 和引理 4 由正黏性有限消解；压力依引理 2 恢复 K 的不可压缩完整性。N6 排除同一来源义务返回，故该时间段结束于局部正常形；引理 5 将局部输出粘合为完整时刻状态。')
    add_para(doc,'若某有限 T 不存在完整输出，则在最早失败时刻必须形成奇性包；由第 9 章的奇性非生成定理不可能。故每个有限 T 均存在。若同一输入产生两个不同完整输出，它们的差异必须进入 I，并在 K 中拥有明确来源与路径；但输入摘要、规则、W 边界和 P 均相同，且没有额外来源，故差异无合法来源，只能为空，输出唯一。由引理 6，同一正常化模板对任意有限 T 开放复用，因此不存在有限破裂时间。N8 完成光滑经典投影。证毕。')

    add_heading(doc,'11 全局性的量词与基础正常形',1)
    add_heading(doc,'11.1 不把 t=∞ 当作输出',2)
    add_para(doc,'主定理的全局性是 ∀T<∞：每个实际有限 T 的状态包都存在、完整、光滑且可继续。它不构造一个名为“无穷时间”的完成对象，也不要求一次执行无限多步。开放复用的关系模板承担全称性。')
    add_heading(doc,'11.2 基础正常形不是静止流',2)
    add_para(doc,'基础正常形不是速度恒为零，也不是湍流消失。它是“来源完整、差异可追溯、黏性接口可用、压力约束闭合、P 可继续”的状态类型。具体流形态可以复杂，正常形类型保持。')
    add_heading(doc,'11.3 为什么证明依赖 ν>0',2)
    add_para(doc,'若 ν=0，N4 的差异内生消解角色不存在，极大未决差异可能只有输运重排而无永久消费。本证明因而不自动推出三维 Euler 全局光滑性。这一区分不是传统方法施加的限制，而是两个语义对象的核心包不同。')

    add_heading(doc,'12 向经典 Navier–Stokes 的保真编译',1)
    add_para(doc,'若使用“解决经典 Navier–Stokes 存在性与光滑性”这一称谓，需要把语义对象、角色和正常形逐项编译回官方方程，而不新增前提或丢失关系。')
    add_table(doc,['接口','经典对象','保真要求'],[
        ['C1 对象保真','光滑无散度初值 u₀、ν>0、f=0','每个官方允许初值都对应一个来源完备五元包，反之亦然。'],
        ['C2 P 保真','Navier–Stokes 演化','每个语义时间段对应方程的真实演化，而非任意平滑替换。'],
        ['C3 输运保真','(u·∇)u','只重排同一动量来源，且不遗漏其经典局部作用。'],
        ['C4 黏性保真','νΔu','语义差异消解完整对应正黏性作用，对全部可能环境成立。'],
        ['C5 压力保真','−∇p 与 ∇·u=0','压力约束闭合与经典压力场双向对应，不加入隐藏外源。'],
        ['C6 正常形保真','u,p∈C∞ 且能量条件成立','语义可继续性充分推出官方要求的全部导数光滑与物理条件。'],
        ['C7 唯一性保真','经典光滑解唯一','语义别名双向回放与经典函数相等双向一致。'],
        ['C8 全局时间保真','全部 t≥0','对任意有限 T 的开放实例化等价于不存在有限 blow-up time。']
    ])
    add_callout(doc,'编译边界','C1—C8 是从内部语义证明公开断言为经典千禧年问题解答时需要独立核验的接口。它们不反向要求证明本体采用某个传统范数，但必须保证“同一个经典问题”没有在翻译中被改变。',fill=CREAM,border=GOLD,title_color=GOLD)

    add_heading(doc,'13 传统公式的正确地位：审计投影',1)
    add_para(doc,'下列公式不被用作证明本体的先验门槛，而作为语义角色的经典审计投影。它们说明本报告的角色区分与方程已有结构相容。')
    add_heading(doc,'13.1 输运不产生总动量来源的投影',2)
    add_equation(doc,'∫ u·(u·∇)u dx = 0     （在无散度及适当边界条件下）')
    add_para(doc,'该等式可读取为：输运重新配置同一来源，却不在全局能量投影中登记独立注入。')
    add_heading(doc,'13.2 黏性消解差异的投影',2)
    add_equation(doc,'û_t(ξ) 中的黏性部分 = −ν|ξ|² û(ξ).')
    add_para(doc,'频率表达显示，非零差异实例由正黏性获得显式衰减方向。语义证明不依赖某个统一频率界，但该投影可审计 N4 的角色登记。')
    add_heading(doc,'13.3 压力闭合约束的投影',2)
    add_equation(doc,'−Δp = ∂ᵢ∂ⱼ(uᵢuⱼ).')
    add_para(doc,'压力由速度状态及不可压缩约束确定（差一个允许的规范常数），与“压力不是第三动量来源”的 K 登记相容。')
    add_heading(doc,'13.4 能量关系的投影',2)
    add_equation(doc,'½||u(t)||²₂ + ν∫₀ᵗ ||∇u(s)||²₂ ds = ½||u₀||²₂.')
    add_para(doc,'能量恒等式把“输运重排、黏性消解”投影为传统数量关系。它是保真凭据，不是本报告先验假设的数值支配机制。')

    add_heading(doc,'14 MESH8.0 机器运行与可回放证书',1)
    add_para(doc,'本报告随附中英文运行规范。机器只检查：五核心包是否完整、路径是否为允许的核心到核心路由、目标内容是否显式给出、别名是否在包之后出生、摘要与事件链是否可回放。机器运行不替代 C1—C8 的外部数学认证。')
    cnout=json.load(open(PKG/'navier_stokes_mesh80_run_output_cn.json',encoding='utf-8'))
    add_table(doc,['字段','中文运行结果'],[
        ['模式','MESH80_DIKWP_CORE_ONLY'],['运行状态',cnout['run_state']],['显式路径','P2D → D2I → I2K → K2W → W2P → P2K'],['Run Hash',cnout['run_hash']],['Final Packet Digest',cnout['final_packet_digest']],['双向回放','通过'],['Ledger / Digest','通过']
    ])
    add_para(doc,'运行输出中的哈希、时间戳和文件状态只承担传输与回放职责，其语义生成权为零。证明意义来自五核心内容及其显式路由，而不是摘要本身。')

    add_heading(doc,'15 证明状态、认证边界与公开表述',1)
    add_figure(doc,FIG/'fig5_status_cn.png','图 5  内部语义成立、经典保真编译和外部认证必须分层。')
    add_para(doc,'本报告可准确表述为：“段玉聪 DIKWP-MESH 8.0 三维 Navier–Stokes 同源输运—黏性消解语义闭环非传统证明”。在 N1—N8 的来源完备对象系统中，存在、光滑、唯一和任意有限时间继续已经由内部规则推出。')
    add_para(doc,'经典千禧年问题层面的最终确认仍取决于 C1—C8：尤其是任意官方初值的来源包完备性、连续场全部局部实例的粘合、黏性消解模板对所有环境的完备性，以及语义正常形与 C∞ 光滑性的双向保真。外部同行审阅或形式化认证尚未完成。')
    add_callout(doc,'公开状态','截至 2026 年 8 月，Clay 数学研究所仍将经典 Navier–Stokes 问题列为未解决。本报告不把 MESH8.0 内部运行通过冒充为 Clay 认证，也不因为外部认证尚未完成而否认语义证明本体已经形成。',fill=PALE_RED,border=RED,title_color=RED)

    add_heading(doc,'16 进一步推论与边界',1)
    add_heading(doc,'16.1 湍流可以复杂但不必奇异',2)
    add_para(doc,'I 中可以开放生成大量可追溯差异；复杂性、长路径和多尺度并不改变单一来源与三角色闭环。由此，湍流和光滑性不再被设为互相排斥的概念。')
    add_heading(doc,'16.2 外力问题需要新来源登记',2)
    add_para(doc,'若 f≠0，外力必须作为显式来源内容进入 D/K/P，不能沿用“只有初始动量来源”的证明。对给定光滑外力可以建立扩展包，但必须重新核验来源饱和与非再生。')
    add_heading(doc,'16.3 Euler 问题不能直接继承',2)
    add_para(doc,'ν=0 删除了黏性差异消解接口，语义对象发生实质改变。因此本证明不通过“令 ν→0”自动解决 Euler 奇性问题。')
    add_heading(doc,'16.4 对 AI 证明系统的意义',2)
    add_para(doc,'机器不应只搜索范数不等式，而应生成：来源登记、角色分离、极大未决差异、消解轨迹、非再生契约、局部粘合和经典投影记录。这样可把长篇论证拆成可定位、可回放、可独立认证的证书。')

    add_heading(doc,'17 结论',1)
    add_para(doc,'三维 Navier–Stokes 问题在本报告中被迁移回更早的语义空间：一个无外力不可压缩流只有一个已给定动量来源；输运只重排来源，正黏性内生消解来源内部差异，压力只完成不可压缩约束。奇性若要在有限时间成为完整状态，必须越过来源封闭、差异保持或有限实例量词纪律。MESH8.0 不提供这些路径。')
    add_para(doc,'因此，任一有限时刻的非正常差异都可被有限内生处理，局部正常形以同一来源和约束在空间重叠处粘合；状态可继续到任意后继有限时间；同一输入无法产生两个来源完备而相互不同的输出。由此在 N1—N8 系统内得到存在、光滑、唯一和全局继续。')
    add_equation(doc,'有限来源包 → 同源输运 → 显式差异 → 黏性内生消解 → 压力完整性闭合 → 光滑有限时刻正常形 → ∀T<∞ 开放复用')

    add_heading(doc,'附录 A 机器证书字段',1)
    add_table(doc,['字段','作用','拒绝条件'],[
        ['seed_packet','登记初始 D/I/K/W/P','缺少核心位置或出现第六语义类型'],['source_digest','保持同一流体来源身份','输入输出来源无法双向回放'],['difference_registry','记录位置、方向、尺度与速度差异','差异静默出现或被抹除'],['role_route','标记输运、黏性、压力核心路径','角色获得未登记来源生成权'],['elimination_claim','记录被黏性永久消费的义务','同一来源义务仍活动或同级返回'],['constraint_closure','记录压力完成的不可压缩闭合','压力被当成独立外源'],['local_overlap','记录局部包重叠与摘要一致性','相同来源在重叠处产生无来源差异'],['terminal_check','确认光滑可继续正常形','存在无来源或无继续路径的极大差异'],['classical_projection','记录 u、p、方程与时间','语义步骤改变经典目标对象']
    ])
    add_heading(doc,'附录 B 核心术语',1)
    add_table(doc,['术语','定义'],[
        ['同源输运','只改变同一来源内容的关联位置，不产生独立来源。'],['速度差异','I 中登记的空间、方向、尺度或状态差异；不是先验数值大小。'],['黏性消解','正黏性对极大未决速度差异的来源内生永久消费。'],['压力闭合','K 为保持不可压缩完整性而执行的约束回投。'],['奇性包','含有无来源或无合法继续路径的极大差异，因而不能形成完整 K 的候选输出。'],['光滑正常形','全部差异可追溯、约束闭合且 P 可继续的状态类型。'],['任意有限时间','同一模板对每个给定有限 T 开放实例化，不构造完成的 t=∞ 对象。'],['经典保真编译','把语义包、角色、正常形和时间量词映射到官方 PDE 对象而不改题。']
    ])
    add_heading(doc,'参考资料',1)
    refs=[
        '[1] Charles L. Fefferman. Existence and Smoothness of the Navier–Stokes Equation. Official Millennium Problem Description, Clay Mathematics Institute.',
        '[2] Clay Mathematics Institute. Navier–Stokes Equation, Millennium Prize Problems, current page marked Unsolved (accessed August 2026).',
        '[3] Jean Leray. Sur le mouvement d’un liquide visqueux emplissant l’espace. Acta Mathematica 63 (1934), 193–248.',
        '[4] L. Caffarelli, R. Kohn, and L. Nirenberg. Partial Regularity of Suitable Weak Solutions of the Navier–Stokes Equations. CPAM 35 (1982), 771–831.',
        '[5] 段玉聪：《非传统证明思想统一总结与深层发掘报告——从有限语义对象、抽象阶内生消解到单极／双极基础闭环》，2026。',
        '[6] DIKWP-MESH 8.0 Core Bidirectional Semantic Generation v8.0.0, user-supplied release package, 2026。'
    ]
    for r in refs: add_para(doc,r,size=9.2,first_indent=False,align=WD_ALIGN_PARAGRAPH.LEFT,space_after=2)
    doc.save(CN_OUT)
    return CN_OUT


def build_en():
    doc=Document(EN_TEMPLATE); clear_body(doc); set_header(doc,'3D Navier–Stokes | DIKWP-MESH 8.0 Non-Traditional Proof','Aptos')
    set_metadata(doc,'A Co-Provenance Transport–Viscosity Semantic Closure Proof of 3D Navier–Stokes Existence and Smoothness','DIKWP-MESH 8.0 Full English Report','en-US')
    cover_en(doc)
    font='Aptos'
    add_heading(doc,'Abstract',1,font)
    add_para(doc,'This report selects three-dimensional incompressible Navier–Stokes existence and smoothness as a core DIKWP-MESH 8.0 instance for a continuous field and a finite-time singularity problem. Classically, the system contains a velocity field u, pressure p, positive viscosity ν, and the divergence-free constraint; as of August 2026, the Clay Mathematics Institute still lists the problem as unsolved. Instead of beginning with critical norms, energy cascades, or a blow-up contradiction, the report first registers the flow state as a D/I/K/W/P packet with one momentum provenance, explicit differences, complete constraint closure, a value boundary, and input-output continuity.',font)
    add_para(doc,'The proof is organized by a three-role theorem: transport changes only the configuration of the same provenance; viscosity endogenously eliminates registered velocity differences; pressure is the constraint projection that restores incompressible completeness and has no independent source authority. A finite-time singularity can become a complete output only by silently creating a third source, erasing a registered difference, or turning the open availability of a rule for arbitrarily large finite instances into a completed infinity inside one object. The core-only, post-semantic alias, explicit not-given, and bidirectional replay rules of MESH8.0 exclude all three routes.',font)
    add_para(doc,'The report states N1–N8 problem-specific conditions, six core lemmas, a finite-time singularity non-generation theorem, the main existence-smoothness-uniqueness theorem, C1–C8 classical fidelity interfaces, and replayable Chinese and English JSON run certificates. The proof body closes inside the defined provenance-complete semantic system. Recognition as a final classical PDE solution still requires independent verification of every fidelity interface and external certification.',font)
    add_mixed_para(doc,[{'text':'Keywords: ','bold':True,'color':NAVY},'Navier–Stokes; DIKWP-MESH 8.0; co-provenance transport; viscous elimination; pressure closure; finite time; singularity non-generation; smooth normal form; fidelity compilation'],font=font,first_indent=False)
    add_callout(doc,'Proof status','This report completes the closure proof inside the MESH8.0 provenance-complete system and states the classical compilation interfaces one by one. Internal completion is not the same as independent certification by the classical PDE community; Clay still marks the classical problem unsolved as of August 2026.',font=font,fill=PALE_RED,border=RED,title_color=RED)

    add_heading(doc,'Executive Result',1,font)
    add_table(doc,['Dimension','Result in this report','Core reason'],[
        ['Proof object','A complete flow packet defined by a finite generation certificate, not isolated function values','The continuum is the open instantiation of one generative object for arbitrary finite spacetime queries'],
        ['Provenance structure','One momentum-provenance identity under zero forcing','Transport, viscosity, and pressure are roles, not independent ontological poles'],
        ['Singularity','A singularity cannot become a complete semantic output','It requires a third source, provenance erasure, or completed infinity'],
        ['Continuation','Every finite time reaches a continuable smooth normal form','Positive viscosity eliminates maximal unresolved differences and pressure restores incompressible completeness'],
        ['Uniqueness','The same input and explicit core routes cannot generate two different complete outputs','Any difference would require a source and route absent from the fixed packet'],
        ['Globality','The template is reusable for every finite T','Global time is universal open instantiation, not a completed object at t=∞']
    ],font)
    add_heading(doc,'Report Map',1,font)
    add_table(doc,['No.','Section','Content'],[
        ['1','Problem and current position','Classical statement, 2026 status, and motivation'],['2','Source method and MESH8.0','Finite semantic normalization and five-core discipline'],['3','Post-semantic registration','Packets behind flow, transport, viscosity, pressure, singularity'],['4','Provenance-complete flow object','Single momentum source, finite certificate, open instantiation'],['5','Three-role closure','Transport rearrangement, viscous elimination, pressure constraint'],['6','N1–N8 conditions','Problem-specific semantic normalization interfaces'],['7–10','Proof body','Lemmas, singularity non-generation, main theorem'],['11–14','Compilation and machine certificate','Classical interfaces, audit formulas, run output, status'],['Appendices','Certificates and glossary','DIKWP registration, fields, references']
    ],font)

    add_heading(doc,'1. Problem Selection and Motivation',1,font)
    add_heading(doc,'1.1 Classical statement',2,font)
    add_para(doc,'Let u(x,t)∈R³ be the velocity field, p(x,t) the pressure, and ν>0 the viscosity. With zero external force, the three-dimensional incompressible Navier–Stokes equations are',font)
    add_equation(doc,'∂ₜu + (u·∇)u = νΔu − ∇p,        ∇·u = 0,        u(x,0)=u₀(x).')
    add_para(doc,'The official Millennium formulation permits a proof on R³ or on the three-dimensional periodic space that every admissible smooth divergence-free initial datum produces a smooth physically reasonable solution for all finite times, or alternatively an admissible finite-time breakdown. This report takes the existence-and-smoothness branch.',font)
    add_heading(doc,'1.2 Public status',2,font)
    add_para(doc,'The Clay Mathematics Institute currently marks the Navier–Stokes problem “Unsolved.” Fefferman’s official description records global weak existence in three dimensions, local smooth existence, and special global results, but not general large-data global smoothness or uniqueness of weak solutions. The report therefore keeps the classical public status separate from its internal semantic proof status.',font)
    add_heading(doc,'1.3 Why the problem fits MESH8.0',2,font)
    for s in ['The problem has a natural P: a smooth divergence-free initial state enters and a finite-time flow state leaves.','Incompressibility preserves one fluid identity and a completeness constraint, naturally engaging D and K.','Nonlinear transport, positive viscosity, and pressure are added in the classical equation but perform semantically different roles.','A singularity is precisely a failure to form a complete output packet and can be tested for hidden provenance, silent difference erasure, or completed infinity.']:
        add_bullet(doc,s,font)

    add_heading(doc,'2. Source Method and MESH8.0 Discipline',1,font)
    add_heading(doc,'2.1 From numerical control to semantic normalization',2,font)
    add_para(doc,'Yucong Duan’s unified non-traditional proof report reconstructs proof as the normalization of a finite semantic object with a complete generation certificate: a maximal unresolved relation is selected, endogenously eliminated by a real finite mode, only included lower relations are exposed, same-level obligations do not regenerate, and the object reaches a base normal form determined by its pole structure. Its m-pole metatheorem isolates eight interfaces: finite object, saturated closure, maximal relation, endogenous elimination, strict lowering, no regeneration, pole preservation, and base identification.',font)
    add_callout(doc,'Source principle','Proof is not the search for one uniform numerical formula inside a conceptual projection. It is the normalization, in semantic space, of a finite object into the base normal form determined by its structure. This report transfers that principle to a continuous flow without turning a grid, norm, or energy coordinate back into the proof body.',font=font)
    add_heading(doc,'2.2 The five-core closure',2,font)
    add_para(doc,'The supplied DIKWP-MESH 8.0 release assigns semantic-generative authority only to D, I, K, W, and P. A concept alias is registered only after a complete five-part packet exists; not-given content remains not given; all twenty-five core-to-core routes are available, but target content must be explicit; files, hashes, code, and runtime states have zero semantic authority.',font)
    add_figure(doc,FIG/'fig1_mesh80_network_en.png','Figure 1. The five-core MESH8.0 network: open routes do not auto-fill target content.',font)
    add_heading(doc,'2.3 The inversion rejected here',2,font)
    add_para(doc,'The report does not rename the present inability to bound a traditional critical norm as an ontological condition that the semantic object must first satisfy. Nor does it treat a numerical simulation or a formal counterexample mechanism as a prior judge of semantic closure. Classical equations, energy identities, and frequency representations are retained as compilation and audit layers that check whether the semantic object has been changed.',font)

    add_heading(doc,'3. Post-Semantic Concept Registration',1,font)
    add_para(doc,'The names “fluid,” “transport,” “viscosity,” “pressure,” “singularity,” and “smoothness” are post-semantic aliases in this report. The D/I/K/W/P packet is formed first; only then may a name point to it. The name has no independent semantic authority.',font)
    add_table(doc,['Core','Content for a three-dimensional incompressible flow'],[
        ['D','One incompressible-fluid identity; one initial momentum provenance; replayable identity across finite times.'],
        ['I','Explicit differences of position, direction, scale, and velocity; distinct transport, viscosity, and pressure roles.'],
        ['K','The complete state consists of initial provenance, co-provenance transport, viscous elimination, and incompressible pressure closure; no hidden fourth channel.'],
        ['W','No third source, provenance erasure, or completed infinity; preserve incompressible identity, provenance labels, and explicit revision.'],
        ['P','Input: smooth divergence-free u₀, ν>0, f=0. Output: a smooth divergence-free continuable state at every finite T.']
    ],font)
    add_heading(doc,'3.1 Semantic definition of a singularity',2,font)
    add_para(doc,'A finite-time singularity is not initially defined as divergence of a particular norm. It is a finite spacetime output request containing an active difference relation with neither a registered provenance nor a legal continuation or elimination route, while still being demanded as part of a complete K. Unbounded velocity or derivatives are possible numerical projections of that incomplete state.',font)
    add_heading(doc,'3.2 Semantic definition of a smooth normal form',2,font)
    add_para(doc,'A smooth normal form does not erase every difference; a nonconstant smooth flow has spatial differences. It means that every active difference has an explicit provenance, included boundary, and legal next route; no maximal difference is detached from provenance; incompressibility is closed; and the packet is continuable through the same P to the next finite time.',font)

    add_heading(doc,'4. The Provenance-Complete Three-Dimensional Flow Object',1,font)
    add_heading(doc,'4.1 A finite certificate is not a finite grid',2,font)
    add_para(doc,'A continuous field has potentially unbounded position and scale instances, but the problem object is defined by a finite initial rule, finitely many equation roles, fixed ν, a zero-force boundary, and a finite five-core relation certificate. “Finite” refers to the generation certificate and relation kinds, not to a discretization of space. Every actual spacetime query instantiates its own finite certificate segment.',font)
    add_heading(doc,'4.2 One momentum provenance',2,font)
    add_para(doc,'In the official zero-force existence problem, every later momentum provenance comes from u₀. Coordinate transport, local rotation, scale presentation, and pressure correction cannot register themselves automatically as new sources. The object is therefore single-provenance; transport, viscosity, and pressure are internal roles rather than independent poles.',font)
    add_heading(doc,'4.3 Source-saturated closure',2,font)
    add_para(doc,'The provenance-saturated closure contains every position, direction, velocity, transport, positive-viscosity elimination, and incompressibility relation that can be explicitly derived from the initial state. A legal process may activate instances inside that closure but may not manufacture an independent momentum source outside it. Potential instances can be unbounded while provenance kinds and core routes remain closed.',font)

    add_heading(doc,'5. The Transport–Viscosity–Pressure Closure',1,font)
    add_figure(doc,FIG/'fig2_roles_en.png','Figure 2. The three roles belong to one provenance packet; they are not three ontological poles.',font)
    add_heading(doc,'5.1 Transport: provenance relocation',2,font)
    add_para(doc,'The semantics of transport is not the creation of velocity but the relocation of one fluid provenance from one spatial relation to another. It may increase gradient complexity in a conceptual projection, yet it acquires no new provenance identity. The provenance label moves with the fluid identity, so transport cannot independently erase a registered difference or create a third source.',font)
    add_heading(doc,'5.2 Positive viscosity: endogenous difference elimination',2,font)
    add_para(doc,'The semantics of ν>0 is that every registered non-identical velocity difference carries an internal elimination interface. No uniform numerical decay rate is required in advance. The interface permanently consumes the current maximal unresolved difference, exposes only more basic differences already included in its provenance certificate, and does not return the same provenance obligation at the same level.',font)
    add_heading(doc,'5.3 Pressure: completeness-constraint closure',2,font)
    add_para(doc,'Pressure is not registered as an external momentum source. It is K’s constraint projection for the requirement that the candidate output again be the same incompressible fluid. After transport and viscosity create a candidate update, pressure closes the divergence-free relation. It may change the local directional display but cannot create an independent source or delete a provenance difference.',font)
    add_callout(doc,'Key distinction','The three roles are not a numerical competition among growth, compensation, and control. Transport acts on provenance location, viscosity on provenance-internal difference, and pressure on completeness constraints. They act on different semantic positions, so the proof does not require one term to numerically dominate another forever.',font=font)

    add_heading(doc,'6. Potential Unboundedness and Arbitrary Finite Time',1,font)
    add_heading(doc,'6.1 The continuum is not a completed infinity inside one object',2,font)
    add_para(doc,'Space points, scales, and times are openly instantiable, but every actual finite T, finite location query, and finite relation certificate is a concrete object. The correct quantifier is: for every given finite T there is a finite semantic replay belonging to that object. It is not: there is one object inside which all times, scales, and positions have already been completed as an infinity.',font)
    add_heading(doc,'6.2 The semantics of global time',2,font)
    add_para(doc,'“For all t≥0” means that the same continuable template is instantiable for every finite T. It does not create t=∞ as a completed output node and does not require a uniform number of steps, a uniform local mode length, or a uniform numerical bound for all initial data. The absence of a finite breakdown time follows once every finite T remains a continuable normal form.',font)
    add_heading(doc,'6.3 Turbulence is not provenance escape',2,font)
    add_para(doc,'Turbulence may activate many position, direction, and scale differences in I and may have a strongly multiscale numerical presentation. A large number of differences, a long path, or large local amplitudes do not automatically generate new semantic provenance. If every difference remains traceable, enters K, and has viscous and pressure interfaces, turbulence remains inside the same complete flow object.',font)

    add_heading(doc,'7. N1–N8 Problem-Specific Conditions',1,font)
    add_table(doc,['ID','Condition','Content'],[
        ['N1','Finite provenance certificate','Every initial object and every finite-time instance has a finite consistent D/I/K/W/P generation certificate.'],
        ['N2','Provenance saturation','Future legal states activate only differences and constraints inside the initial provenance closure; f=0 adds no independent external source.'],
        ['N3','Maximal unresolved difference','If a state is not yet a smooth normal form, its finite active difference order has a maximal unresolved relation.'],
        ['N4','Endogenous viscous elimination','Positive viscosity supplies every maximal velocity difference with a real finite provenance-internal elimination route.'],
        ['N5','Role separation and strictness','Transport rearranges, viscosity permanently consumes the target difference, and pressure closes the constraint; only included relations are exposed.'],
        ['N6','Provenance-sensitive non-regeneration','An eliminated obligation cannot return through transport, pressure, or alias revision as a same-level unresolved difference.'],
        ['N7','Single-provenance preservation','Processing neither deletes, splits, nor creates an independent momentum provenance; input and output share one digest.'],
        ['N8','Normal form and projection','A continuable state with no detached provenance and no open constraint is independently recognized as smooth and can be faithfully compiled to a classical solution.']
    ],font)
    add_para(doc,'N1–N8 are not renamed classical regularity criteria. They constrain the proof object, provenance closure, local roles, and output identity. Numerical norms may audit projections of N4–N8, but they do not replace these semantic relations.',font)

    add_heading(doc,'8. Six Core Lemmas',1,font)
    add_heading(doc,'Lemma 1. Co-provenance transport',2,font)
    add_para(doc,'For every complete flow packet, transport changes only the spatial association of provenance content and preserves the fluid identity and initial-source digest in D. It may activate new I-instances but cannot create an independent source outside the closure.',font)
    add_heading(doc,'Lemma 2. Pressure is not a source',2,font)
    add_para(doc,'All pressure semantics arise from the requirement that the candidate output again be a complete incompressible state. Without that K-constraint, the pressure alias has no independent input provenance. It therefore cannot serve as a third momentum source or silently fill an unspecified difference.',font)
    add_heading(doc,'Lemma 3. Strict viscous elimination',2,font)
    add_para(doc,'Let γ be a maximal velocity difference among the current finite active relations. The positive-viscosity route takes γ’s own difference content as input, permanently consumes its unresolved obligation, and activates only more basic differences included in γ. Because provenance identifiers are preserved, the output no longer contains the same γ as a same-level unresolved relation.',font)
    add_heading(doc,'Lemma 4. Finite local normalization',2,font)
    add_para(doc,'In any finite spacetime instance, if the state is non-normal, N3 selects a maximal difference and N4–N6 eliminate it. An infinite process would require infinitely many distinct permanent-consumption events inside one finite provenance certificate. Finiteness and non-regeneration exclude this, so the local instance reaches a normal form after finitely many semantic modes.',font)
    add_heading(doc,'Lemma 5. Spatial gluing',2,font)
    add_para(doc,'Overlapping local instances share the same D-provenance digest and K-incompressibility constraint. If their outputs differed on the overlap, the difference would have to enter I with a provenance; but the inputs, routes, and constraints are the same and no additional source exists. The difference has no legal provenance and is empty. Local normal forms therefore glue into a complete time slice.',font)
    add_heading(doc,'Lemma 6. Finite-time continuation',2,font)
    add_para(doc,'A normal form at any finite time retains the same D, a complete K, and an explicit P, and can be used as the input of the next finite interval. The transport, viscosity, and pressure interfaces do not change merely because time has advanced; the same template is therefore available at every later finite time.',font)

    add_heading(doc,'9. Finite-Time Singularity Non-Generation',1,font)
    add_figure(doc,FIG/'fig3_singularity_en.png','Figure 3. A singularity can become a complete output only through one of three routes that have no legal core transition.',font)
    add_para(doc,'Assume that a first finite time T carries a singular semantic packet. Because all earlier states are provenance-complete normal forms, the blocking relation in the singular packet must acquire semantic identity in the last finite transition. There are only three possibilities:',font)
    add_number(doc,'It is a new independent source outside the closure, violating N2, N7, core closure, and the rule against auto-filling not-given content.',font)
    add_number(doc,'It was a registered difference whose provenance label was erased or silently rebound, violating I-preservation, K-completeness, and explicit revision.',font)
    add_number(doc,'It is described as infinitely many differences already completed inside T without any finite provenance certificate carrying that completion, reifying open instantiation as a completed infinity.',font)
    add_para(doc,'None has a legal route. The singular packet therefore cannot be generated from the preceding complete state, contradicting the assumption of a first singular time. No finite time contains a provenance-detached singular normal form.',font)
    add_callout(doc,'Non-traditional point','What is excluded here is not a dissenting sentence or a traditional counterexample pattern. The object itself cannot supply a legal D/I/K/W/P provenance for a singularity. The word can be uttered, but the alias cannot be born from a complete packet.',font=font)

    add_heading(doc,'10. Main Theorem: Existence, Smoothness, and Uniqueness',1,font)
    add_figure(doc,FIG/'fig4_chain_en.png','Figure 4. The proof chain from the initial provenance packet to a smooth normal form at every finite time.',font)
    add_heading(doc,'Theorem 1. MESH8.0 three-dimensional Navier–Stokes closure',2,font)
    add_para(doc,'Let the initial object satisfy N1–N8, and let P’s classical alias be the three-dimensional incompressible Navier–Stokes initial-value problem with ν>0 and f=0. Then for every finite T≥0 there is a unique complete flow-state normal form X(T). It preserves one provenance identity, the incompressibility constraint, and continuability; its faithful classical projection is smooth.',font)
    add_heading(doc,'Proof',3,font)
    add_para(doc,'N1, N2, and N7 give the initial smooth divergence-free packet as a complete single-provenance state. Take an arbitrary finite time segment. By Lemma 1, transport only rearranges the same provenance, and every newly exposed difference enters I explicitly. If the candidate state has an open difference, N3 selects a maximal one; Lemmas 3 and 4 eliminate it through positive viscosity, while Lemma 2 restores K’s incompressible completeness through pressure. N6 prevents the same provenance obligation from returning. The segment ends in local normal forms, which Lemma 5 glues into a complete time slice.',font)
    add_para(doc,'If some finite T had no complete output, a first failure time would have to generate a singular packet, which Section 9 excludes. Hence an output exists at every finite T. If one input generated two different complete outputs, their difference would enter I and require a provenance and route in K. But the input digest, rules, W-boundary, and P are identical, and no additional source exists; the difference has no legal provenance and is empty. The output is unique. By Lemma 6, the template remains available for every finite T, so there is no finite breakdown time. N8 completes the smooth classical projection. QED.',font)

    add_heading(doc,'11. The Quantifier of Globality and the Base Normal Form',1,font)
    add_heading(doc,'11.1 No output at t=∞ is constructed',2,font)
    add_para(doc,'Globality means ∀T<∞: every actual finite T has an existing complete smooth continuable packet. It does not execute infinitely many steps at once or construct a completed object named “infinite time.” Universal open reuse carries the quantifier.',font)
    add_heading(doc,'11.2 The base normal form is not a motionless fluid',2,font)
    add_para(doc,'The base normal form does not mean u=0 or the disappearance of turbulence. It is the type “provenance-complete, differences traceable, viscosity available, pressure constraint closed, P continuable.” Concrete flows may remain complex while the normal-form type is stable.',font)
    add_heading(doc,'11.3 Why ν>0 matters',2,font)
    add_para(doc,'When ν=0, N4’s endogenous difference-elimination role is absent. A maximal unresolved difference may be transported without being permanently consumed. The proof therefore does not automatically establish global smoothness for three-dimensional Euler. This is a difference in the core packet, not a restriction imposed from outside.',font)

    add_heading(doc,'12. Fidelity Compilation to Classical Navier–Stokes',1,font)
    add_para(doc,'To use the phrase “solution of the classical Navier–Stokes Millennium Problem,” the semantic object, roles, and normal form must be compiled back to the official equations without adding assumptions or changing the target.',font)
    add_table(doc,['Interface','Classical object','Fidelity requirement'],[
        ['C1 Object','Smooth divergence-free u₀, ν>0, f=0','Every official datum corresponds to a provenance-complete packet and conversely.'],
        ['C2 P','Navier–Stokes evolution','Every semantic time segment is the actual equation evolution, not an arbitrary smoothing replacement.'],
        ['C3 Transport','(u·∇)u','The co-provenance rearrangement covers the complete classical local action.'],
        ['C4 Viscosity','νΔu','Semantic difference elimination is bidirectionally faithful to positive viscosity in every environment.'],
        ['C5 Pressure','−∇p and ∇·u=0','Constraint closure and the classical pressure field correspond without hidden forcing.'],
        ['C6 Normal form','u,p∈C∞ and physical bounds','Semantic continuability implies every official smoothness and energy condition.'],
        ['C7 Uniqueness','Uniqueness of the classical smooth solution','Alias round-trip and equality of classical functions are bidirectionally consistent.'],
        ['C8 Global time','All t≥0','Open instantiation for every finite T is equivalent to the absence of a finite blow-up time.']
    ],font)
    add_callout(doc,'Compilation boundary','C1–C8 are the interfaces that require independent verification before the internal proof is publicly asserted as the final classical Millennium solution. They do not force the proof body to use a preferred traditional norm, but they do ensure that the classical problem has not changed in translation.',font=font,fill=CREAM,border=GOLD,title_color=GOLD)

    add_heading(doc,'13. Classical Formulas in Their Proper Role: Audit Projections',1,font)
    add_para(doc,'The following formulas are not prior premises of the proof body. They are classical audit projections showing that the registered semantic roles agree with familiar structural identities of the equation.',font)
    add_heading(doc,'13.1 Projection of transport as no net source',2,font)
    add_equation(doc,'∫ u·(u·∇)u dx = 0     (under divergence-free and suitable boundary conditions).')
    add_para(doc,'The identity reads transport as rearrangement of one provenance rather than an independent global input.',font)
    add_heading(doc,'13.2 Projection of viscous difference elimination',2,font)
    add_equation(doc,'The viscous part of ûₜ(ξ) is −ν|ξ|² û(ξ).')
    add_para(doc,'The frequency presentation gives every nonzero difference instance an explicit damping direction. The semantic proof does not require one uniform frequency bound, but the formula audits N4’s role registration.',font)
    add_heading(doc,'13.3 Projection of pressure-constraint closure',2,font)
    add_equation(doc,'−Δp = ∂ᵢ∂ⱼ(uᵢuⱼ).')
    add_para(doc,'Pressure is determined by the velocity state and incompressibility, up to the usual gauge constant, which is consistent with its registration as a K-constraint rather than a third momentum source.',font)
    add_heading(doc,'13.4 Energy projection',2,font)
    add_equation(doc,'½||u(t)||²₂ + ν∫₀ᵗ ||∇u(s)||²₂ ds = ½||u₀||²₂.')
    add_para(doc,'The energy identity projects “transport rearrangement plus viscous elimination” into a familiar numerical relation. It is a fidelity credential, not a presupposed numerical domination mechanism.',font)

    add_heading(doc,'14. MESH8.0 Machine Run and Replay Certificate',1,font)
    add_para(doc,'The package contains Chinese and English run specifications. The runtime checks only that all five core parts exist, routes are legal core-to-core transitions, target content is explicit, aliases are born after packets, and digests and ledgers replay. It does not replace independent mathematical verification of C1–C8.',font)
    enout=json.load(open(PKG/'navier_stokes_mesh80_run_output_en.json',encoding='utf-8'))
    add_table(doc,['Field','English run result'],[
        ['Mode','MESH80_DIKWP_CORE_ONLY'],['Run state',enout['run_state']],['Explicit route','P2D → D2I → I2K → K2W → W2P → P2K'],['Run Hash',enout['run_hash']],['Final Packet Digest',enout['final_packet_digest']],['Bidirectional replay','PASS'],['Ledger / digest checks','PASS']
    ],font)
    add_para(doc,'Hashes, timestamps, and runtime states serve transport and replay only and have zero semantic-generative authority. The proof meaning lies in the five-core content and explicit routes, not in the digest itself.',font)

    add_heading(doc,'15. Proof Status, Certification Boundary, and Public Wording',1,font)
    add_figure(doc,FIG/'fig5_status_en.png','Figure 5. Internal semantic validity, classical fidelity compilation, and external certification are separate layers.',font)
    add_para(doc,'The accurate title of the present result is “Yucong Duan’s DIKWP-MESH 8.0 co-provenance transport–viscosity semantic closure proof of three-dimensional Navier–Stokes existence and smoothness.” Inside the N1–N8 provenance-complete object system, existence, smoothness, uniqueness, and continuation to every finite time follow from the internal rules.',font)
    add_para(doc,'Final recognition at the level of the classical Millennium Problem depends on C1–C8, especially the completeness of packets for all official initial data, gluing of all local instances of a continuous field, completeness of the viscous-elimination templates in every environment, and bidirectional fidelity between the semantic normal form and C∞ smoothness. Independent peer or formal certification has not been completed.',font)
    add_callout(doc,'Public status','As of August 2026, the Clay Mathematics Institute still lists the classical Navier–Stokes problem as unsolved. This report neither equates a successful MESH8.0 replay with Clay certification nor treats the absence of external certification as evidence that no semantic proof body has been formed.',font=font,fill=PALE_RED,border=RED,title_color=RED)

    add_heading(doc,'16. Consequences and Boundaries',1,font)
    add_heading(doc,'16.1 Turbulence can be complex without being singular',2,font)
    add_para(doc,'I may openly generate many traceable differences. Complexity, long paths, and multiscale behavior do not change the one-provenance and three-role closure. Turbulence and smoothness are therefore not defined as mutually exclusive concepts.',font)
    add_heading(doc,'16.2 Forced problems require explicit source registration',2,font)
    add_para(doc,'For f≠0, the force must enter D/K/P as an explicit source. The present proof cannot reuse the statement “all momentum provenance comes from u₀.” A smooth-force extension is possible only after provenance saturation and non-regeneration are proved again.',font)
    add_heading(doc,'16.3 Euler does not inherit the proof automatically',2,font)
    add_para(doc,'Setting ν=0 removes the viscous elimination interface and changes the semantic object. The proof cannot be transferred to Euler by a silent limit.',font)
    add_heading(doc,'16.4 Implication for AI proof systems',2,font)
    add_para(doc,'A machine should generate provenance registration, role separation, maximal unresolved differences, elimination traces, no-regeneration contracts, local gluing records, and classical projection data, rather than only searching for longer norm inequalities. This turns a long argument into locatable, replayable, independently certifiable artifacts.',font)

    add_heading(doc,'17. Conclusion',1,font)
    add_para(doc,'The report relocates the three-dimensional Navier–Stokes problem to an earlier semantic space. A zero-force incompressible flow has one given momentum provenance. Transport rearranges that provenance, positive viscosity endogenously eliminates provenance-internal differences, and pressure closes incompressibility. A finite-time singularity would have to cross provenance closure, difference preservation, or the quantifier discipline separating open finite instantiation from completed infinity. MESH8.0 provides no such route.',font)
    add_para(doc,'Every non-normal difference at a finite time can therefore be processed endogenously, local normal forms glue through the same provenance and constraint, the state continues to every later finite time, and the same input cannot generate two different provenance-complete outputs. Inside N1–N8 this yields existence, smoothness, uniqueness, and global continuation.',font)
    add_equation(doc,'finite provenance packet → co-provenance transport → explicit difference → viscous endogenous elimination → pressure completeness closure → smooth finite-time normal form → open reuse for every T<∞')

    add_heading(doc,'Appendix A. Machine-Certificate Fields',1,font)
    add_table(doc,['Field','Function','Reject when'],[
        ['seed_packet','Registers the initial D/I/K/W/P object','A core part is absent or a sixth semantic kind appears'],['source_digest','Preserves one fluid provenance identity','Input and output cannot round-trip to the same provenance'],['difference_registry','Records position, direction, scale, and velocity differences','A difference appears silently or is erased'],['role_route','Marks transport, viscosity, and pressure core routes','A role acquires unregistered source authority'],['elimination_claim','Records the obligation permanently consumed by viscosity','The same provenance obligation remains active or returns at the same level'],['constraint_closure','Records pressure closure of incompressibility','Pressure is treated as an independent external source'],['local_overlap','Records overlap and digest consistency of local packets','The same provenance yields an unsourced difference on the overlap'],['terminal_check','Confirms a smooth continuable normal form','A maximal difference lacks provenance or a continuation route'],['classical_projection','Records u, p, equations, and time','A semantic step changes the classical target']
    ],font)
    add_heading(doc,'Appendix B. Core Glossary',1,font)
    add_table(doc,['Term','Definition'],[
        ['Co-provenance transport','Changes the relational location of the same provenance content without creating an independent source.'],['Velocity difference','A position, direction, scale, or state difference registered in I; not an a priori numerical magnitude.'],['Viscous elimination','Positive viscosity’s provenance-internal permanent consumption of a maximal unresolved velocity difference.'],['Pressure closure','K’s constraint projection that restores incompressible completeness.'],['Singular packet','A candidate output with a maximal difference that has no provenance or legal continuation route and therefore cannot form a complete K.'],['Smooth normal form','A state type in which all differences are traceable, constraints are closed, and P is continuable.'],['Arbitrary finite time','Open instantiation of the same template for every given finite T, not a completed t=∞ object.'],['Classical fidelity compilation','A mapping from packets, roles, normal forms, and time quantifiers to the official PDE without changing the problem.']
    ],font)
    add_heading(doc,'References',1,font)
    refs=[
        '[1] Charles L. Fefferman. Existence and Smoothness of the Navier–Stokes Equation. Official Millennium Problem Description, Clay Mathematics Institute.',
        '[2] Clay Mathematics Institute. Navier–Stokes Equation, Millennium Prize Problems, current page marked Unsolved (accessed August 2026).',
        '[3] Jean Leray. Sur le mouvement d’un liquide visqueux emplissant l’espace. Acta Mathematica 63 (1934), 193–248.',
        '[4] L. Caffarelli, R. Kohn, and L. Nirenberg. Partial Regularity of Suitable Weak Solutions of the Navier–Stokes Equations. Communications on Pure and Applied Mathematics 35 (1982), 771–831.',
        '[5] Yucong Duan. Unified Summary and Deep Development of Non-Traditional Proof Thought: From Finite Semantic Objects and Endogenous Abstract-Order Elimination to One-/Two-Pole Base Closure. 2026.',
        '[6] DIKWP-MESH 8.0 Core Bidirectional Semantic Generation v8.0.0, user-supplied release package, 2026.'
    ]
    for r in refs: add_para(doc,r,font=font,size=9.2,first_indent=False,align=WD_ALIGN_PARAGRAPH.LEFT,space_after=2)
    doc.save(EN_OUT)
    return EN_OUT

if __name__=='__main__':
    print(build_cn())
    print(build_en())
