import tiktoken

from utils import load_json
import openai
import os
import pandas as pd

from dotenv import load_dotenv
def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

GPT_MODEL = "gpt-3.5-turbo"

def count_num_tokens(text, model = GPT_MODEL):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def halved_by_delimiter(string, delimiter = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = count_num_tokens(string)
        halfway = total_tokens // 2
        best_diff = halfway
        for i, chunk in enumerate(chunks):
            left = delimiter.join(chunks[: i + 1])
            left_tokens = count_num_tokens(left)
            diff = abs(halfway - left_tokens)
            if diff >= best_diff:
                break
            else:
                best_diff = diff
        left = delimiter.join(chunks[:i])
        right = delimiter.join(chunks[i:])
        return [left, right]
    

def truncated_text(
        text,
        model,
        max_tokens,
        print_warning = True
):
    """Trucate a text to a maximum number of tokens"""
    encoding = tiktoken.encoding_for_model(model)
    encoded_text= encoding.encode(text)
    truncated_text = encoding.decode(encoded_text[:max_tokens])
    if print_warning and len(encoded_text) > max_tokens:
        print(f"Warning: Trucanted text from {len(encoded_text)} token to {max_tokens} tokens.")
    return truncated_text

def split_text_into_subsections(
        section,
        max_tokens,
        model = GPT_MODEL,
        max_recursion = 5
):
    """
    Split text into list subsections, each with no more than max_tokens
    """
    title, text = section
    string = "\n\n".join([title,text])
    num_tokens_in_text = count_num_tokens(string)
    print("\n\nnum_tokens_in_text:", num_tokens_in_text)
    if num_tokens_in_text <= max_tokens:
        return [text]
    elif max_recursion == 0:
        return truncated_text(string, model=model, max_tokens=max_tokens)
    else:
        for delimiter in ["\n\n", "\n", "."]:
            left, right = halved_by_delimiter(string, delimiter=delimiter)
            print("left:", left)
            print("\n\nright:", right)
            
            if left == "" or right == "":
                continue
            else:
                results = []
                for half in [left, right]:
                    half_subsection = (title, half)
                    half_strings = split_text_into_subsections(
                        half_subsection,
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                    return [text]
                    results.extend(half_strings)
                return results
    
    return [truncated_text(string, model=model, max_tokens=max_tokens)]


MAX_TOKENS = 600

text_subsections = []
general_topics_subsections = []
type_sources = []

topics = load_json("topics_finals.json")
faqs = load_json("faq/faq_json.json")

""" for topic in topics:
    title = topic["topic"]
    content = topic["content"]
    print("title:", title)
    section = (title, content)
    subsections = split_text_into_subsections(section, max_tokens=MAX_TOKENS)
    print(f"Divido en {len(subsections)} secciones")
    text_subsections.extend(subsections)
    general_topics_subsections.extend([title] * len(subsections))
    type_sources.extend(["document"] * len(subsections))
embeddings = []

print("\nNumero de secciones encontradas:", len(text_subsections))

for faq in faqs:
    text_faq = faq["topic"].title() + "\n" + faq["question"] + "\n" + faq["answer"]
    text_subsections.append(text_faq)
    general_topics_subsections.append(faq["topic"])
    type_sources.append("faq")
print("\nNumero de secciones encontradas:", len(text_subsections)) """

text = """            TRASLADO INTERNO
        (del Reglamento de Matrícula Aprobado R.R. N° 0570 del 29.03.22)

Art. 16° De la convalidación de Asignaturas y su aplicación 
 
La Convalidación de Asignatura es el acto académico y administrativo mediante el cual la UNI a través de la Escuela Profesional correspondiente, aplica un sistema de equivalencia y reconoce como válidas las asignaturas de contenido similar y número de créditos igual o similar al de otro Plan de Estudios con respecto a uno vigente en la Escuela Profesional. Para que proceda, los respectivos sílabos de las asignaturas a convalidar deberán coincidir al menos en un 75% de su contenido y de horas dictadas. Las asignaturas para convalidar deben tener igual número de créditos o diferir como máximo en uno (01). Por excepción, la convalidación de una asignatura con mayor profundidad en el contenido quedará a la consideración del secretario académico de la facultad.  
El estudiante tiene derecho a solicitar la convalidación de asignaturas en los siguientes casos: 
 
a. Traslado  Interno: Es un procedimiento mediante el cual el ingresante de una Escuela Profesional de la UNI pasa a otra especialidad de su Facultad o de otra, cumpliendo los requisitos académicos y administrativos. 
 
Art. 17° El plazo para que las Escuelas Profesionales efectúen los procesos de asignación de Plan de Estudios y convalidación será de hasta cinco (05) días útiles computados desde: 
 
    • En el caso de Traslado Interno, desde la aprobación del Consejo de Facultad o autorización del Decano (con cargo a dar cuenta al siguiente Consejo), previos al Examen de Admisión.  
    • En el caso de Reincorporación, desde la recepción del expediente.  
    • En el caso de Traslados Externos, Segunda Profesión y por convenio nacional o internacional, la Dirección de Admisión (DIAD), bajo responsabilidad, deberá entregar a las Facultades; con copia a DIRCE (para la generación de códigos), los expedientes de estos ingresantes, a más tardar en cinco (05) días hábiles de concluido el examen de admisión respectivo. La facultad dispondrá de cinco (05) días útiles más, para las convalidaciones; para lo cual disponen de los respectivos formatos en la plataforma SIGA-DIRCE. 
 
La DIRCE deberá procesar las convalidaciones realizadas por las Facultades en un plazo máximo de cinco (05) días útiles computados desde su recepción.  
 
Para los Traslados Internos del segundo semestre de cada año, no se consideran las asignaturas cursadas en el semestre inmediato anterior, pues la presentación del trámite es antes del cierre del ciclo. Si las hubiese, el estudiante solicitará su convalidación posterior a la Verificación de Matrícula y las matrículas adicionales, si fuera el caso. En segundo semestre, no se admite rezago en los Traslados.  
 
Art.  53°  Los  ingresantes  a  la  UNI  por  traslado  interno  o  externo,  graduados,  titulados,  y  por convenios, solicitarán a la Escuela Profesional correspondiente su primera matrícula, la misma que se realizará a través de la Oficina de Estadística de la Facultad, en coordinación con la DIRCE-UNI.


Detalle del procedimiento de Traslado Interno: 

    1. El interesado presentará su solicitud a través del intranet alumnos / tramites; hasta la fecha que indica el calendario académico. Adjuntando lo siguiente: 
        − Comprobante de pago por el concepto de Traslado Interno. 
        − Ficha Académica 
    2. La Escuela, dentro del 1er día útil de presentada verificará documentos y requisitos propios, registrará el expediente y remitirá correo de recepción al interesado. Luego, si fuere necesario, solicitará a otras Escuelas Profesionales de la UNI la remisión de sílabos pertinentes, si el director lo solicita y atenderá similares solicitudes de otras Escuelas  
    3. El director de Escuela o la Comisión de Matrícula analizará las solicitudes y haciendo uso del formato disponible en la web DIRCE, inscribirá las convalidaciones pertinentes, según el Avance Curricular del alumno, las notas y las normas de Convalidación. Si quedan notas no registradas, serán motivo de convalidación posterior a la matrícula.  
    4. Con  la  autorización  del  director,  el  expediente  es  enviado  al  Decano  y  posteriormente presentarlo ante el Consejo de Facultad para su aprobación (mediante Resolución Decanal) y remisión a la DIRCE.  
    5. La DIRCE ejecutará el cambio de especialidad y/o facultad y las convalidaciones.   
    6. Registradas las convalidaciones, la Oficina de Estadística gestiona la matrícula de los sestudiantes por traslado interno en función a la solicitud de matrícula del director de la Escuela Profesional, finalmente la DIRCE realiza la ejecución de la matrícula en el sistema SIGA. 
    7. No se recibirán solicitudes extemporáneas  """

subsections = split_text_into_subsections(
        section = (text, "Traslado Interno"),
        max_tokens = 600,
        model = GPT_MODEL,
        max_recursion = 5
)

print("Len:", len(subsections))

""" EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50
print("\nNumero de secciones encontradas:", len(text_subsections))
for batch_start in range(0, len(text_subsections), BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, len(text_subsections))
    batch = text_subsections[batch_start:batch_end]
    print(f"Batch {batch_start} to {batch_end-1}")
    response = openai.embeddings.create(model=EMBEDDING_MODEL, input= batch)
    for i, be in enumerate(response.data):
        assert i == be.index  # double check embeddings are in same order as input
    batch_embeddings = [e.embedding for e in response.data]
    embeddings.extend(batch_embeddings)

df = pd.DataFrame({"type_source": type_sources ,"topic": general_topics_subsections, "text": text_subsections, "embedding": embeddings})

SAVE_PATH = "./kb/topics.csv"

df.to_csv(SAVE_PATH, index=False) """