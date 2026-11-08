import os, json, time, math, platform
import flet as ft

# ===================== 内置数据（不依赖 xlsx） =====================
MATERIALS = [
    {"id":1,"name":"钢/铁","density":7.85,"eq":1.0,"hvl160":11,"hvl225":12,"hvl450":14,"typical":"碳钢、铸铁、不锈钢"},
    {"id":2,"name":"铝合金","density":2.7,"eq":0.18,"hvl160":3.5,"hvl225":4.2,"hvl450":5.0,"typical":"压铸铝、航空铝"},
    {"id":3,"name":"钛合金(TC4)","density":4.5,"eq":0.71,"hvl160":7.5,"hvl225":8.5,"hvl450":10,"typical":"航空发动机、植入物"},
    {"id":4,"name":"铜","density":8.96,"eq":1.35,"hvl160":14,"hvl225":16,"hvl450":19,"typical":"电极、散热"},
    {"id":5,"name":"不锈钢(316)","density":8.0,"eq":1.05,"hvl160":12,"hvl225":13,"hvl450":15,"typical":"食品、医疗"},
    {"id":6,"name":"镁合金","density":1.74,"eq":0.12,"hvl160":2.8,"hvl225":3.2,"hvl450":4.0,"typical":"轻量化壳体"},
    {"id":7,"name":"陶瓷(Al2O3)","density":3.9,"eq":0.85,"hvl160":8,"hvl225":9,"hvl450":11,"typical":"轴承、装甲"},
    {"id":8,"name":"PEEK","density":1.32,"eq":0.08,"hvl160":2.0,"hvl225":2.4,"hvl450":3.0,"typical":"医用植入、航天"},
    {"id":9,"name":"碳纤维复材","density":1.6,"eq":0.15,"hvl160":3.0,"hvl225":3.6,"hvl450":4.2,"typical":"结构件"},
    {"id":10,"name":"玻璃纤维","density":2.0,"eq":0.22,"hvl160":3.8,"hvl225":4.5,"hvl450":5.2,"typical":"壳体"},
    {"id":11,"name":"铅","density":11.3,"eq":1.8,"hvl160":0.8,"hvl225":0.9,"hvl450":1.1,"typical":"屏蔽件"},
    {"id":12,"name":"锌合金","density":6.6,"eq":0.45,"hvl160":6,"hvl225":7,"hvl450":8,"typical":"压铸件"},
    {"id":13,"name":"镍基高温合金","density":8.5,"eq":1.2,"hvl160":13,"hvl225":14,"hvl450":16,"typical":"涡轮叶片"},
    {"id":14,"name":"混凝土","density":2.4,"eq":0.5,"hvl160":6.5,"hvl225":7.5,"hvl450":9,"typical":"建筑"},
    {"id":15,"name":"塑料(ABS)","density":1.05,"eq":0.05,"hvl160":1.5,"hvl225":1.8,"hvl450":2.2,"typical":"外壳"},
]

WORKPIECES = [
    {"name":"铝合金轮毂","mat":"铝合金","thk":"8-25","target":"气孔/裂纹","defect":50,"kv":225,"focus":"20-50μm","current":"0.1-0.3mA","power":8,"mode":"DR+CT","filter":"0.5mmCu","cycle":"90-180s","tip":"微焦点CT看气孔，薄壁用低kV保对比度"},
    {"name":"压铸铝壳体","mat":"铝合金","thk":"3-15","target":"缩孔/冷隔","defect":30,"kv":160,"focus":"10-30μm","current":"0.05-0.2mA","power":5,"mode":"CT","filter":"0.2mmCu","cycle":"60-120s","tip":"壁厚不均要分段重建"},
    {"name":"钛合金锻件","mat":"钛合金(TC4)","thk":"20-60","target":"夹杂/未熔","defect":20,"kv":300,"focus":"50-100μm","current":"0.2-0.5mA","power":15,"mode":"DR+CT","filter":"1mmCu","cycle":"120-300s","tip":"高原子序数，kV别太低否则穿不透"},
    {"name":"航空发动机叶片","mat":"钛合金(TC4)","thk":"2-10","target":"微裂纹/冷却孔","defect":10,"kv":225,"focus":"5-15μm","current":"0.02-0.1mA","power":3,"mode":"Micro-CT","filter":"0.1mmCu","cycle":"200-600s","tip":"放大比>10，像素尺寸<5μm"},
    {"name":"钢结构焊缝","mat":"钢/铁","thk":"10-40","target":"未熔合/气孔","defect":50,"kv":300,"focus":"100-200μm","current":"0.5-1mA","power":25,"mode":"DR","filter":"1mmCu+1mmAl","cycle":"10-30s","tip":"双壁透照注意几何不清晰度"},
    {"name":"铸铁缸体","mat":"钢/铁","thk":"15-50","target":"缩松/裂纹","defect":100,"kv":450,"focus":"200-500μm","current":"1-3mA","power":80,"mode":"DR+CT","filter":"2mmCu","cycle":"30-90s","tip":"厚大件用450kV，关注散射伪影"},
    {"name":"不锈钢食品阀","mat":"不锈钢(316)","thk":"5-20","target":"夹杂/晶间腐蚀","defect":30,"kv":225,"focus":"20-50μm","current":"0.1-0.3mA","power":8,"mode":"CT","filter":"0.5mmCu","cycle":"120-240s","tip":"表面光洁度影响伪影，需滤波"},
    {"name":"碳纤维无人机臂","mat":"碳纤维复材","thk":"2-8","target":"分层/纤维断","defect":20,"kv":160,"focus":"10-30μm","current":"0.05-0.2mA","power":4,"mode":"CT","filter":"无滤波","cycle":"180-360s","tip":"低kV高对比，避免金属滤波"},
    {"name":"PEEK植入物","mat":"PEEK","thk":"3-12","target":"孔隙率/缺陷","defect":15,"kv":160,"focus":"5-20μm","current":"0.02-0.1mA","power":3,"mode":"Micro-CT","filter":"无滤波","cycle":"240-480s","tip":"密度低，常规kV易过透"},
    {"name":"陶瓷轴承","mat":"陶瓷(Al2O3)","thk":"5-20","target":"气孔/裂纹","defect":10,"kv":225,"focus":"10-30μm","current":"0.05-0.2mA","power":5,"mode":"CT","filter":"0.3mmCu","cycle":"200-400s","tip":"高硬脆材料，微焦点看微裂纹"},
    {"name":"铜散热器","mat":"铜","thk":"3-15","target":"气孔/虚焊","defect":40,"kv":225,"focus":"30-80μm","current":"0.1-0.4mA","power":10,"mode":"CT","filter":"0.5mmCu","cycle":"120-240s","tip":"吸收强，适当提kV"},
    {"name":"镁合金壳体","mat":"镁合金","thk":"2-10","target":"缩孔/氧化夹渣","defect":25,"kv":160,"focus":"10-30μm","current":"0.05-0.2mA","power":4,"mode":"CT","filter":"0.2mmCu","cycle":"90-180s","tip":"极轻材料，低kV"},
    {"name":"PCB板","mat":"塑料(ABS)","thk":"1-4","target":"虚焊/BGA空洞","defect":5,"kv":100,"focus":"2-10μm","current":"0.01-0.05mA","power":1,"mode":"Micro-CT","filter":"无滤波","cycle":"300-600s","tip":"看BGA用2D切片+三维重建"},
    {"name":"铅屏蔽件","mat":"铅","thk":"5-30","target":"浇铸缺陷","defect":100,"kv":450,"focus":"200-500μm","current":"1-3mA","power":80,"mode":"DR","filter":"2mmCu","cycle":"20-60s","tip":"极难穿透，优先DR"},
    {"name":"锌压铸件","mat":"锌合金","thk":"3-15","target":"冷隔/气孔","defect":40,"kv":225,"focus":"20-60μm","current":"0.1-0.3mA","power":8,"mode":"CT","filter":"0.3mmCu","cycle":"60-150s","tip":"薄壁件低kV"},
    {"name":"高温合金涡轮盘","mat":"镍基高温合金","thk":"30-80","target":"疏松/夹杂","defect":30,"kv":450,"focus":"100-300μm","current":"0.5-1.5mA","power":60,"mode":"CT+DR","filter":"2mmCu","cycle":"180-360s","tip":"厚大高密，必须450kV级"},
    {"name":"混凝土构件","mat":"混凝土","thk":"50-200","target":"空洞/钢筋位置","defect":500,"kv":0,"focus":"0.4-1.0mm","current":"3-10mA","power":200,"mode":"DR","filter":"3mmCu","cycle":"5-20s","tip":"超厚件，需MeV加速器（本工具仅给方向）"},
]

SOURCES = [
    {"name":"微焦点(低能)","kv":"40-120kV","power":"<1W","focus":"2-10μm","steel":"<5mm","use":"电子/小零件显微CT"},
    {"name":"小焦点(中能)","kv":"120-225kV","power":"<20W","focus":"20-100μm","steel":"5-25mm","use":"常规精密件CT"},
    {"name":"中焦点","kv":"225-300kV","power":"20-80W","focus":"100-500μm","steel":"25-50mm","use":"中等厚度件DR/CT"},
    {"name":"大焦点(高能)","kv":"300-450kV","power":"80-300W","focus":"0.5-2mm","steel":"50-100mm","use":"厚钢件DR"},
    {"name":"MeV加速器","kv":">1MeV","power":">1kW","focus":"1-3mm","steel":">100mm","use":"超大厚度/混凝土"},
    {"name":"平板探测器(小视野)","kv":"-","power":"-","focus":"-","steel":"-","use":"高分辨CT"},
    {"name":"线阵探测器","kv":"-","power":"-","focus":"-","steel":"-","use":"大件高速DR"},
]

# ===================== 计算逻辑 =====================
def calc_params(mat_id, t):
    m = next((x for x in MATERIALS if x["id"]==mat_id), None)
    if not m: return None
    eq = round(t*m["eq"], 2)
    if eq <= 3: kv=100
    elif eq <= 10: kv=160
    elif eq <= 20: kv=225
    elif eq <= 45: kv=300
    elif eq <= 70: kv=450
    else: kv=0
    hvl = m["hvl225"] if eq>10 else m["hvl160"]
    try:
        att = round(2**(eq/hvl), 1)
    except:
        att = 9999
    if kv==0:
        focus="需MeV焦点(1-3mm)"; current="3-10mA"; src="MeV加速器"
    elif kv<=100:
        focus="2-10μm"; current="0.01-0.05mA"; src="微焦点(低能)"
    elif kv<=160:
        focus="10-30μm"; current="0.05-0.2mA"; src="小焦点(中能)"
    elif kv<=225:
        focus="20-100μm"; current="0.1-0.5mA"; src="小焦点(中能)"
    elif kv<=300:
        focus="100-300μm"; current="0.3-1mA"; src="中焦点"
    else:
        focus="0.5-2mm"; current="1-3mA"; src="大焦点(高能)"
    return {"mat":m,"eq_thk":eq,"rec_kv":kv,"hvl":hvl,"attenuation":att,
            "focus":focus,"current":current,"source":src}

# ===================== 导出图片（安卓兼容） =====================
def _export_dir():
    if platform.system()=="Android":
        try:
            from android.storage import app_storage_path
            d = os.path.join(app_storage_path(), "Pictures")
        except Exception:
            d = os.path.join(os.path.expanduser("~"), "cache")
    else:
        d = os.path.join(os.path.expanduser("~"), "Pictures" if platform.system()=="Windows" else "Downloads")
    os.makedirs(d, exist_ok=True)
    return d

def export_calc_png(r, matched):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6,9)); ax.axis("off")
    y=0.97
    ax.text(0.5,y,"工业CT 选型结果",ha="center",va="top",fontsize=16,fontweight="bold")
    y-=0.07
    for line in [
        f"材质: {r['mat']['name']}",
        f"等效钢厚度: {r['eq_thk']} mm",
        f"推荐电压: {r['rec_kv']} kV" if r['rec_kv']>0 else "推荐电压: 需MeV加速器",
        f"衰减倍数: {r['attenuation']}",
        f"焦点: {r['focus']}",
        f"电流: {r['current']}",
        f"源档位: {r['source']}",
    ]:
        ax.text(0.05,y,line,ha="left",va="top",fontsize=12); y-=0.055
    if matched:
        y-=0.02
        ax.text(0.05,y,"匹配工件:",ha="left",va="top",fontsize=12,fontweight="bold",color="red"); y-=0.05
        for n in matched[:3]:
            ax.text(0.1,y,f"• {n}",ha="left",va="top",fontsize=11,color="red"); y-=0.045
    fp=os.path.join(_export_dir(), f"CT选型_{int(time.time())}.png")
    fig.savefig(fp,dpi=200,bbox_inches="tight"); plt.close(fig)
    return fp

def export_wp_png(w):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6,9)); ax.axis("off"); y=0.97
    ax.text(0.5,y,w["name"],ha="center",va="top",fontsize=16,fontweight="bold"); y-=0.07
    for line in [f"材质:{w['mat']}",f"壁厚:{w['thk']}mm",f"目标:{w['target']}",f"缺陷:{w['defect']}μm",
                 f"电压:{w['kv']}kV",f"焦点:{w['focus']}",f"模式:{w['mode']}",f"滤波:{w['filter']}",f"💡{w['tip']}"]:
        ax.text(0.05,y,line,ha="left",va="top",fontsize=12); y-=0.055
    fp=os.path.join(_export_dir(),f"CT工件_{w['name']}_{int(time.time())}.png")
    fig.savefig(fp,dpi=200,bbox_inches="tight"); plt.close(fig); return fp

# ===================== 状态 =====================
page_ref=None

def save(k,v):
    try: page_ref.client_storage.set(k,json.dumps(v,ensure_ascii=False))
    except: pass
def load(k,d):
    try:
        s=page_ref.client_storage.get(k); return json.loads(s) if s else d
    except: return d

# ===================== UI =====================
def main(page: ft.Page):
    global page_ref
    page_ref=page
    page.title="工业CT选型速查"
    page.scroll=ft.ScrollMode.AUTO

    fav=set(load("favorites",[])); cmp=load("compare",[]); hist=load("calc_history",[])
    recent_m=load("recent_materials",[]); recent_w=load("recent_workpieces",[])

    area=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO)

    # ---- Tab1 选型 ----
    mat_dd=ft.Dropdown(label="材质",width=380,options=[ft.dropdown.Option(str(m["id"]),m["name"]) for m in MATERIALS])
    thk=ft.TextField(label="厚度mm",value="10",width=380,keyboard_type=ft.KeyboardType.NUMBER)
    res=ft.Card(visible=False)

    def on_calc(e):
        if not mat_dd.value or not thk.value: return
        try: t=float(thk.value)
        except: return
        r=calc_params(int(mat_dd.value),t)
        if not r: return
        matched=[]
        mn=r["mat"]["name"]
        for i,w in enumerate(WORKPIECES):
            sc=0
            if mn in w["mat"] or w["mat"] in mn: sc+=2
            try:
                a,b=w["thk"].split("-"); lo,hi=float(a),float(b)
                if lo<=t<=hi: sc+=2
            except: pass
            if r["rec_kv"]>0 and w["kv"]>0 and abs(r["rec_kv"]-w["kv"])<=50: sc+=1
            if sc>=2: matched.append((sc,i,w))
        matched.sort(key=lambda x:-x[0]); matched=matched[:3]
        mnames=[w["name"] for _,_,w in matched]

        hist.insert(0,{"id":int(time.time()*1000),"time":time.strftime("%Y-%m-%d %H:%M"),
                       "mat_name":mn,"thickness":t,"eq_thk":r["eq_thk"],"rec_kv":r["rec_kv"],
                       "source":r["source"],"matched":mnames})
        hist[:]=hist[:50]; save("calc_history",hist)
        recent_m[:]=[mn]+[x for x in recent_m if x!=mn]; recent_m[:]=recent_m[:10]; save("recent_materials",recent_m)

        def exp(e):
            try:
                fp=export_calc_png(r,mnames)
                page.snack_bar=ft.SnackBar(content=ft.Text("已导出 "+os.path.basename(fp))); page.snack_bar.open=True
            except Exception as ex:
                page.snack_bar=ft.SnackBar(content=ft.Text("导出失败:"+str(ex))); page.snack_bar.open=True
            page.update()

        kv = f"{r['rec_kv']} kV" if r['rec_kv']>0 else "需MeV加速器"
        res.content=ft.Container(padding=15,content=ft.Column([
            ft.Row([ft.Text("计算结果",weight=ft.FontWeight.BOLD,size=14,color=ft.Colors.GREY_600),
                    ft.IconButton(icon=ft.Icons.CAMERA_ALT,on_click=exp,icon_color=ft.Colors.BLUE_700)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(f"材质: {mn}"),
            ft.Text(f"等效钢: {r['eq_thk']} mm"),
            ft.Text(f"推荐电压: {kv}",weight=ft.FontWeight.BOLD,size=16),
            ft.Text(f"衰减倍数: {r['attenuation']}"),
            ft.Text(f"焦点: {r['focus']}"),
            ft.Text(f"电流: {r['current']}"),
            ft.Text(f"源档位: {r['source']}",weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE),
            ft.Divider(),
            *[ft.TextButton(f"▸ {w['name']}",on_click=lambda e,i=i: jump_wp(i)) for _,i,w in matched]
        ]))
        res.visible=True; page.update()

    def set_mat(n):
        for m in MATERIALS:
            if m["name"]==n: mat_dd.value=str(m["id"]); page.update(); break

    recent_chips_row = ft.Row([ft.Chip(label=ft.Text(n,size=11),on_select=lambda e,n=n: set_mat(n)) for n in recent_m[:6]],wrap=True) if recent_m else ft.Text("")

    tab1=ft.Column([ft.Container(height=10),
        ft.Text("最近材质:",size=12,color=ft.Colors.GREY),
        recent_chips_row,
        ft.Container(height=6),mat_dd,ft.Container(height=10),thk,
        ft.Container(height=10),ft.ElevatedButton("计算",width=380,height=45,on_click=on_calc),
        ft.Container(height=20),res],scroll=ft.ScrollMode.AUTO,expand=True)

    # ---- Tab2 工件速查 ----
    wp_search=ft.TextField(label="搜索",width=380,on_change=lambda e: wp_filter(e))
    wp_dd=ft.Dropdown(label="工件",width=380,options=[ft.dropdown.Option(str(i),w["name"]) for i,w in enumerate(WORKPIECES)])
    wp_card=ft.Card(visible=False)

    def wp_filter(e):
        kw=wp_search.value.strip().lower()
        wp_dd.options=[ft.dropdown.Option(str(i),w["name"]) for i,w in enumerate(WORKPIECES)
                      if not kw or kw in w["name"].lower() or kw in w["mat"].lower() or kw in w["target"].lower()]
        wp_dd.value=None; wp_card.visible=False; page.update()

    def on_wp(e):
        if not wp_dd.value: return
        i=int(wp_dd.value); w=WORKPIECES[i]
        recent_w[:]=[w["name"]]+[x for x in recent_w if x!=w["name"]]; recent_w[:]=recent_w[:10]; save("recent_workpieces",recent_w)
        kv=f"{w['kv']}kV" if w["kv"]>0 else "需MeV"
        def exp(e):
            try:
                fp=export_wp_png(w); page.snack_bar=ft.SnackBar(content=ft.Text("已导出 "+os.path.basename(fp))); page.snack_bar.open=True
            except Exception as ex:
                page.snack_bar=ft.SnackBar(content=ft.Text("导出失败:"+str(ex))); page.snack_bar.open=True
            page.update()
        def fav_toggle(e):
            if i in fav: fav.remove(i)
            else: fav.add(i)
            save("favorites",list(fav)); on_wp(None); page.update()
        def cmp_toggle(e):
            if i in cmp: cmp.remove(i)
            else:
                if len(cmp)>=2: return
                cmp.append(i)
            save("compare",cmp); on_wp(None); page.update()
        wp_card.content=ft.Container(padding=15,content=ft.Column([
            ft.Row([ft.Text(w["name"],size=17,weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE,expand=True),
                    ft.IconButton(icon=ft.Icons.CAMERA_ALT,on_click=exp,icon_color=ft.Colors.BLUE_700)],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Text(f"材质: {w['mat']}"),ft.Text(f"壁厚: {w['thk']}mm"),
            ft.Text(f"目标: {w['target']}"),ft.Text(f"缺陷: {w['defect']}μm"),
            ft.Text(f"电压: {kv}",weight=ft.FontWeight.BOLD),
            ft.Text(f"焦点: {w['focus']}  电流: {w['current']}"),
            ft.Text(f"模式: {w['mode']}  滤波: {w['filter']}"),
            ft.Text(f"💡 {w['tip']}",size=12,italic=True,color=ft.Colors.ORANGE),
            ft.Container(height=8),
            ft.Row([ft.ElevatedButton("★收藏" if i in fav else "☆收藏",on_click=fav_toggle),
                    ft.ElevatedButton("➕对比" if i not in cmp else "✓对比",on_click=cmp_toggle)])
        ]))
        wp_card.visible=True; page.update()
    wp_dd.on_change=on_wp

    tab2=ft.Column([ft.Container(height=10),ft.Text("工件速查",size=16,weight=ft.FontWeight.BOLD),
        wp_search,ft.Container(height=8),wp_dd,ft.Container(height=20),wp_card],scroll=ft.ScrollMode.AUTO,expand=True)

    # ---- 其他Tab ----
    tab3=ft.ListView(expand=True,spacing=8,padding=10,controls=[ft.Card(content=ft.Container(padding=12,content=ft.Column([
        ft.Text(m["name"],weight=ft.FontWeight.BOLD),ft.Text(f"密度{m['density']} 等效{m['eq']} HVL@225:{m['hvl225']}mm")]))) for m in MATERIALS])
    tab4=ft.ListView(expand=True,spacing=8,padding=10,controls=[ft.Card(content=ft.Container(padding=12,content=ft.Column([
        ft.Text(s["name"],weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE),ft.Text(f"{s['kv']} {s['power']} 焦点{s['focus']} 穿透{s['steel']}"),ft.Text(s["use"],size=11,color=ft.Colors.GREY)]))) for s in SOURCES])
    tab5=ft.Column(scroll=ft.ScrollMode.AUTO,expand=True,controls=[ft.Container(padding=15,content=ft.Column([
        ft.Text("公式",weight=ft.FontWeight.BOLD,size=16),
        ft.Text("等效钢=厚度×等效系数"),ft.Text("衰减=2^(等效钢/半值层)"),
        ft.Text("电压: ≤3→100,≤10→160,≤20→225,≤45→300,≤70→450,>70→MeV"),
        ft.Divider(),ft.Text("误区",weight=ft.FontWeight.BOLD,size=16),
        ft.Text("①kV越大越好 ②微焦点一定清 ③电流大更清 ④一台225通吃")]))])

    fav_lv=ft.ListView(expand=True,spacing=8,padding=10)
    def build_fav():
        fav_lv.controls.clear()
        if not fav: fav_lv.controls.append(ft.Text("暂无收藏"))
        for i in sorted(fav):
            w=WORKPIECES[i]
            fav_lv.controls.append(ft.Card(content=ft.Container(padding=12,content=ft.Column([
                ft.Text(w["name"],weight=ft.FontWeight.BOLD),ft.Text(f"{w['mat']} {w['thk']}mm"),
                ft.ElevatedButton("查看",on_click=lambda e,i=i: jump_wp(i))]))))
        page.update()
    tab6=ft.Column([ft.Container(height=10),ft.Text("收藏"),fav_lv],expand=True)

    cmp_col=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO)
    def build_cmp():
        cmp_col.controls.clear()
        if len(cmp)<2: cmp_col.controls.append(ft.Text("选2个工件"))
        else:
            a,b=WORKPIECES[cmp[0]],WORKPIECES[cmp[1]]
            rows=[("材质",a["mat"],b["mat"]),("壁厚",a["thk"],b["thk"]),("目标",a["target"],b["target"]),
                  ("电压",str(a["kv"]),str(b["kv"])),("焦点",a["focus"],b["focus"])]
            for lb,v1,v2 in rows:
                d=v1!=v2
                cmp_col.controls.append(ft.Container(padding=6,bgcolor=ft.Colors.AMBER_50 if d else None,border_radius=6,content=ft.Column([
                    ft.Text(lb,size=11,color=ft.Colors.GREY_600),
                    ft.Row([ft.Text(v1,expand=1,text_align=ft.TextAlign.CENTER,color=ft.Colors.RED if d else ft.Colors.BLACK,weight=ft.FontWeight.BOLD if d else ft.FontWeight.NORMAL),
                            ft.Text(v2,expand=1,text_align=ft.TextAlign.CENTER,color=ft.Colors.RED if d else ft.Colors.BLACK,weight=ft.FontWeight.BOLD if d else ft.FontWeight.NORMAL)])])))
            cmp_col.controls.append(ft.ElevatedButton("清空",on_click=lambda e: (cmp.clear(),save("compare",cmp),build_cmp())))
        page.update()
    tab7=ft.Column([ft.Container(height=10),ft.Text("对比"),cmp_col],expand=True)

    hist_lv=ft.ListView(expand=True,spacing=8,padding=10)
    def build_hist():
        hist_lv.controls.clear()
        if not hist: hist_lv.controls.append(ft.Text("暂无历史"))
        for h in hist:
            kv=f"{h['rec_kv']}kV" if h['rec_kv']>0 else "MeV"
            hist_lv.controls.append(ft.Card(content=ft.Container(padding=12,content=ft.Column([
                ft.Text(f"{h['mat_name']} {h['thickness']}mm  {h['time']}",weight=ft.FontWeight.BOLD),
                ft.Text(f"{kv} 等效{h['eq_thk']}mm {h['source']}")]))))
        page.update()
    tab8=ft.Column([ft.Container(height=10),ft.Text("历史"),hist_lv],expand=True)

    tab9=ft.Column([ft.Container(height=10),ft.Text("说明/数据"),ft.Text("内置15材料/17工件/7源，无xlsx依赖")],expand=True)

    def jump_wp(i):
        wp_dd.value=str(i); on_wp(None)
        page.navigation_bar.selected_index=1
        area.controls.clear(); area.controls.append(tab2); page.update()

    def switch(e):
        idx=int(e.data); area.controls.clear()
        if idx==0: area.controls.append(tab1)
        elif idx==1: area.controls.append(tab2)
        elif idx==2: area.controls.append(tab3)
        elif idx==3: area.controls.append(tab4)
        elif idx==4: area.controls.append(tab5)
        elif idx==5: build_fav(); area.controls.append(tab6)
        elif idx==6: build_cmp(); area.controls.append(tab7)
        elif idx==7: build_hist(); area.controls.append(tab8)
        elif idx==8: area.controls.append(tab9)
        elif idx==9: area.controls.append(tab9)
        page.update()

    page.navigation_bar=ft.NavigationBar(
        selected_index=0,
        on_change=switch,
        destinations=[ft.NavigationBarDestination(icon=ft.Icons.CALCULATE,label="选型"),
            ft.NavigationBarDestination(icon=ft.Icons.SEARCH,label="工件"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST,label="材料"),
            ft.NavigationBarDestination(icon=ft.Icons.FLASH_ON,label="源"),
            ft.NavigationBarDestination(icon=ft.Icons.INFO,label="说明"),
            ft.NavigationBarDestination(icon=ft.Icons.STAR,label="收藏"),
            ft.NavigationBarDestination(icon=ft.Icons.COMPARE,label="对比"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY,label="历史"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK,label="模板"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS,label="数据")])
    area.controls.append(tab1)
    page.add(area)

ft.app(main)
