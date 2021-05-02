import base64
import zlib
import urllib.parse

def define_env(env):
    "Hook function"
    
    @env.macro
    def pyexo(chemin, baseurl="", width="100%", height=480):
        with open(chemin) as fichier:
            exercice = fichier.read()
            exo_comp = zlib.compress(exercice.encode())
            exo_cb64 = base64.urlsafe_b64encode(exo_comp).decode()
            return f"""<iframe src="{baseurl}?clear=titre1:titre2:enonce&exo={exo_cb64}" width={width} height={height}></iframe>"""
    
    @env.macro
    def pyexo_parser(chemin):
        titre1, titre2, enonce, solution, tests, code, indication, unitaires = ["INDEFINI"] * 8
        with open(chemin) as fichier:
            exercice = fichier.read()
            separateur = [ligne for ligne in exercice.split("\n") if ligne.startswith("===")][0] or "==="
            reste = exercice
            titre1, _, reste = reste.partition(separateur)
            titre2, _, reste = reste.partition(separateur)
            enonce, _, reste = reste.partition(separateur)
            solution, _, reste = reste.partition(separateur)
            tests, _, reste = reste.partition(separateur)
            code, _, reste = reste.partition(separateur)
            indication, _, reste = reste.partition(separateur)
            unitaires, _, reste = reste.partition(separateur)
        return {"titre1":titre1, "titre2":titre2, "enonce":enonce, "solution":solution,
                "tests":tests, "code":code, "indication":indication, "unitaires":unitaires}
    
    @env.macro
    def pyexo_titre(chemin):
        infos = pyexo_parser(chemin)
        titre1 = infos["titre1"].replace("\n"," ").replace("\r"," ").strip()
        titre2 = infos["titre2"].replace("\n"," ").replace("\r"," ").strip()
        return f"""{titre1} \- {titre2}"""
    
    @env.macro
    def preparer_markdown(chaine):
        if "<pre>" in chaine:
            chaine = chaine.replace("<pre>","<pre><code>").replace("</pre>","</code></pre>")
        else:
            chaine = chaine.replace("\n"," ").replace("\r"," ")
            for tag in "*_":
                chaine = chaine.replace(tag,"\\"+tag)
        return chaine.strip()

    @env.macro
    def pyexo_enonce(chemin):
        infos = pyexo_parser(chemin)
        enonce = preparer_markdown(infos["enonce"])
        return f"""{enonce}"""
    
    @env.macro
    def pyexo_indication(chemin):
        infos = pyexo_parser(chemin)
        indication = preparer_markdown(infos["indication"])
        indication = indication or "Pas d'indication pour cet exercice."
        return f"""{indication}"""

