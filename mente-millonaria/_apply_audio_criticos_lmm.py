# -*- coding: utf-8 -*-
import re, json

with open('capitulos_data.js', encoding='utf-8') as f:
    content = f.read()

# Kodak
old1 = '"Empresas gigantes como Kodak o Enron quebraron también, a pesar de que miles de empleados y accionistas estaban igual de convencidos de conocerlas bien."'
new1 = '"Enron, que en 2001 se desplomó tras destaparse un fraude contable, y Kodak, que en 2012 tuvo que acogerse a un procedimiento de reestructuración por insolvencia del que salió reducida a una fracción de lo que fue, tenían miles de empleados y accionistas igual de convencidos de conocerlas bien."'
assert old1 in content, "Kodak no encontrado"
content = content.replace(old1, new1, 1)

# C-1
old2 = '"La línea la cruzas cuando mientes sobre los hechos, no cuando organizas los hechos a tu favor (pero dónde está esa línea exactamente depende de tu jurisdicción, y solo un profesional local puede confirmártelo)."'
new2 = ('"La línea no está solo en mentir: ocultar una cuenta, inventar una factura o no declarar un ingreso es evasión, '
        'y suele ser delito. Pero hay un terreno intermedio que conviene conocer: la Administración tributaria puede desmontar '
        'operaciones formalmente correctas y declaradas si concluye que son artificiosas y que su única finalidad razonable '
        'era pagar menos impuestos, sin necesidad de probar que mentiste. Dónde está exactamente esa frontera es una '
        'cuestión técnica que solo un asesor fiscal de tu jurisdicción puede valorar en tu caso."')
assert old2 in content, "C-1 no encontrado"
content = content.replace(old2, new2, 1)

# C-3 (sustituye las 2 oraciones "beneficiarios: la trampa..." y "Si firmaste...")
old3a = ('"beneficiarios: la trampa de los formularios\\n\\nMuchas cuentas (seguros de vida, planes de pensiones) tienen su '
         'propio formulario de \\"beneficiario\\" que sustituye a lo que diga tu testamento."')
new3a = ('"beneficiarios: la trampa de los formularios\\n\\nMuchas cuentas (seguros de vida, planes de pensiones) tienen su '
         'propio formulario de \\"beneficiario\\" que sustituye a lo que diga tu testamento. Es rápido y es eficaz, y por eso '
         'mismo es peligroso: si firmaste ese formulario hace quince años, antes de divorciarte o de tener hijos, sigue '
         'vigente."')
assert old3a in content, "C-3a no encontrado"
content = content.replace(old3a, new3a, 1)

old3b = ('"Si firmaste ese formulario hace quince años, antes de divorciarte o de tener hijos, ese papel manda por encima '
         'de tu testamento actual en la mayoría de jurisdicciones."')
new3b = ('"La buena noticia es que en muchos países, España entre ellos, puedes cambiar esa designación cuando '
         'quieras, incluso en tu testamento. La mala es que nadie lo hará por ti: revisa esos papeles."')
assert old3b in content, "C-3b no encontrado"
content = content.replace(old3b, new3b, 1)

# C-2 insertar nuevo epigrafe sobre la legitima, antes de "Herederos vs."
anchor = '   "Herederos vs.",'
insert = ('   "Lo que tu testamento no puede decidir\\n\\nAntes de sentarte a escribirlo, conviene saber algo que la mayoría '
          'de los libros de finanzas no cuenta: en España, en Suiza y en buena parte de Latinoamérica no puedes '
          'repartir tu patrimonio como quieras.",\n'
          '   "La ley reserva una parte, llamada legítima, a determinados familiares, normalmente hijos y descendientes, '
          'y esa parte está fuera de tu alcance por mucho que la escribas de otro modo. Cuánto es esa parte reservada '
          'cambia radicalmente según dónde vivas. La pregunta que tienes que llevar al notario o al abogado es: '
          '¿qué parte de mi patrimonio puedo repartir libremente según la ley que se me aplica, y qué parte '
          'no?",\n')
assert anchor in content, "anchor Herederos vs. no encontrado"
content = content.replace(anchor, insert + anchor, 1)

with open('capitulos_data.js', 'w', encoding='utf-8') as f:
    f.write(content)

m = re.search(r"const\s+CAPITULOS\s*=\s*(\[.*\])", content, flags=re.DOTALL)
data = json.loads(m.group(1))
print("JSON OK, capitulos:", len(data))
