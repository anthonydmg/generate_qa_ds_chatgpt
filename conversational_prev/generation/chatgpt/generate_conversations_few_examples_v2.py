messages = [ {
    "role":"system", 
    "content": """Eres un asistente de IA especializado en temas de matriculas, tramites y procedimiendo academicos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.
Se te dará un texto tomado de un fragmento del reglamento de matricula y una lista de preguntas que puedan ser respondidas con la informacion delimitada por . 
A continuación se detallan los requisitos para generar conversaciónes entre un usuario y un asistente de IA :
- Cada conversacion debe tener al menos 2 o 3 turnos de preguntas y respuestas de preguntas de la lista de preguntas, que son consultadas por el usuario en la conversacion.
- Se creativo al realizar las consultas de diferentes maneras ajustandolas al contexto de la conversacion entre el asistente de IA y el usuario.
- El usuario en la conversacion debe manejar un lenguaje coloquial propio de un estudiante universitario.- Asegurate el usuario maneje un lenguaje natural propio de un alumno universitario, docente o persona adulta.
- El asistente en la conversarion debe responder las preguntas de menera explicativa y amigable usando al texto tomado de un fragmento del reglamento.
- Evite citar numerales de los reglamentos en las respuestas. Concéntrese brindar la informacion necesaria para justificar o explicar la respuesta.
- Genere al menos 10 conversaciones 
"""}
]

few_shot_examples = [{
    "context": """Reglamento: CAPÍTULO II

CONCEPTOS Y NORMAS DEL PROCESO DE MATRÍCULA

Art. 7 La matrícula es el resultado de un acto formal que es ejecutado personal y voluntariamente por el estudiante (sujeto a verificación posterior), de inscribirse en un período académico; no es obligatorio tomar el máximo de créditos permitidos. Implica el cumplimiento de la Ley Universitaria, el Estatuto, las normas de la UNI y el presente reglamento. La matrícula es responsabilidad exclusiva del estudiante y se realiza semestralmente.

Art. 8° Se define como estudiante regular en un semestre, al estudiante matriculado en no menos de doce (12) créditos del Plan de Estudios de su especialidad, luego del retiro parcial. Se exceptúa a quienes culminen sus estudios en dicho semestre. 

Se define como estudiante en riesgo académico a quien tenga desaprobada una o más asignaturas en dos o tres oportunidades. Previo a su matrícula debe pasar, de manera obligatoria, por un proceso de tutoría académica.

Art. 9° La matrícula, por su oportunidad, puede ser de dos tipos:

	a. Matrícula Regular: cuando se realiza de manera digital, en las fechas establecidas en el calendario de actividades académicas y en no menos de doce (12) créditos. La realizará el estudiante de modo virtual y en estricto orden de mérito. El orden de mérito se establece en base al promedio ponderado de los dos (02) últimos períodos académicos regulares cursados como estudiante regular. 

	b. Matrícula Rezagada: cuando se realiza fuera de las fechas establecidas para la matrícula en la primera semana de clases, fijada en el calendario de actividades académicas. Se realizará exclusivamente a través de la Oficina de Estadística de la respectiva Facultad y debe contar con la autorización del Director de la Escuela Profesional que corresponda. Es la que corresponde a los ingresantes de todo tipo y reincorporados rezagados. Puede solicitar autorización para esta matrícula, todo estudiante que no haya podido ejecutar su matrícula regular Académica. 

Art. 10° La matrícula, por su tratamiento, puede ser de cinco tipos:

	a. Matrícula Libre: Aquella que no tiene condicionamientos: asignaturas a cursar por primera o segunda vez.
	b. Matrícula Condicionada: conforme al Artículo 102º de la Ley Universitaria Nº 30220, y los Art. 251 º, Art. 252º y Art. 253º del Estatuto de la UNI, se presentan los siguientes casos: 
		i. Cuando el estudiante ha desaprobado una misma asignatura dos (02) veces, ORCE la incluirá en la oferta de Matrícula, como obligatoria. En este caso, en la tutoría previa al inicio del semestre a matricularse, se podrá incluir dicha asignatura en el Grupo Cero (ver Art. 11 º, n) y se definirán las demás asignaturas a matricular. Alguna podrá ser obviada sólo si tiene cruce de horario con otra de ciclo inferior. Estas últimas van a matricula regular en las fechas establecidas en el calendario académico de cada Facultad.
		ii. Cuando el estudiante retorna de haber cumplido suspensión de un año, por Bajo Rendimiento Académico, sólo se podrá matricular en un máximo de dos asignaturas desaprobadas por tercera vez; no pudiendo matricularse en ninguna otra asignatura. Podrá solicitar, a través de la Tutoría Obligatoria, su incorporación en el Grupo Cero y su matrícula automática. Si fuese una asignatura y ésta hubiese cambiado de código, será cursada como por primera vez y podrá incluir en su matrícula una segunda asignatura. Si alguna fuese electiva, y no desea aprobarla, podrá solicitar previamente su exoneración. Si por exoneraciones se excluye del riesgo académico, podrá matricularse, en acuerdo con la tutoría, hasta en 15 créditos. Para retornar de manera regular a sus estudios en el ciclo siguiente, el estudiante debe haber aprobado la totalidad de las asignaturas desaprobadas por tercera vez y haber cumplido con el proceso de tutoría. 

En estos dos (02) casos, la matrícula de las asignaturas en riesgo se realizará a pedido del Tutor en el Grupo Cero, en la sección de menor demanda. Las otras asignaturas se matricularán de modo regular, en el turno que corresponda a cada estudiante; siendo verificada por la Comisión de Matricula correspondiente. El alumno que no se presente dentro del calendario a la tutoría no podrá matricularse. 

	c. Matrícula Preferencial. Es la de un grupo previo al primero que está integrado por los estudiantes con un máximo 30 créditos pendientes para concluir su carrera. Esta ventaja se podrá solicitar sólo una vez, también la es, la del Grupo Cero, consolidado por la Oficina de Tutoría. Cada estudiante solicitará con anticipación a su Director de Escuela, que lo incluya en dicho grupo. Este listado se cierra tres días útiles antes del inicio de la matrícula regular; una vez vencido el plazo, este no se admitirá.

	d. Matrícula Especial por Convenio: Es la que corresponde a estudiantes procedentes de intercambio por convenios con universidades nacionales o extranjeras. No requiere señalarse el plan de estudios, ni los requisitos. Se autoriza la matrícula del estudiante mediante Resolución Decana! dirigida a la ORCE, acompañada de la constancia de ingreso emitida por la Oficina Central de Cooperación Internacional y Convenios de la UNI. La ORCE genera código
especial de alumno, previo a la matrícula.""",
    "questions": """
        Preguntas:
            - ¿Si un estudiante se matricula en 14 créditos, es considerado alumno regular?
            - ¿Que es una matricula rezagada?
            - ¿La matrícula, por su oportunidad, de que tipos pueden ser?
            - ¿Cuando se aplica una matricula condicionada?
            - ¿Cuando un estudiante retorna de haber cumplido suspension de un año por Bajo Rendimiento Académico de un anio en cuantas asignaturas como maximo puede matricularse?
            - ¿Un alumno que retorna luego de haber cumplido año por Bajo Rendimiento Académico puede matricularse en 5 asignaturas?
            - ¿En que casos la matrícula de las asignaturas en riesgo se realizará a pedido del Tutor en el Grupo Cero, en la sección de menor demanda?
            - ¿La matricula regular se realiza de manera digital?
            - ¿Cuando se realiza la matricula regular?
            - ¿Como se establece el orden de mérito?
            - ¿El orden de mérito solo considera el ultimo periodo académico regular cursado por el estudiante regular?
        """,
    "response": """
        conversacion 1:
            user: hola
            asistant: Hola, mi nombre es Aerito soy un  asistente de IA especializado en temas de matriculas, tramites y procedimiendo academicos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria. En que puedo ayudarte?
            user: 
    """

},
{
    "context": """CAPÍTULO II

CONCEPTOS Y NORMAS DEL PROCESO DE MATRÍCULA

Art. 11° Para el presente reglamento se entiende por: 

	a. Reincorporación: es el procedimiento que restablece al estudiante la condición de estudiante activo, quien realizó Retiro total, solicitó Reserva de Matrícula o Licencia, o dejó de matricularse un semestre académico o más, teniendo como plazo límite tres (03) años o seis (06) periodos académicos consecutivos o alternos. En caso de periodos académicos alternos estos no excederán de cinco (05) años contados a partir del primer periodo académico en el que dejó de matricularse. Es procedente si no tiene sanción vigente y no ha superado el plazo máximo de Reserva de
Matrícula.

	La reincorporación se presenta según el calendario oficial, a través de la Plataforma SIGA-ORCE.

	b. Verificación, depuración y ratificación de matrícula: proceso que se realiza en la primera semana de clases; mediante el cual el estudiante, luego de efectuar su matrícula regular, solicita al Director de la Escuela Profesional la autorización para incluir o excluir asignaturas. 
	La matrícula en asignaturas solamente procede de acuerdo con el presente reglamento y las asignaturas solicitadas no tengan cruce de horario.
	El estudiante no se podrá retirar de todas las asignaturas matriculadas, por considerarse un retiro total, ni de aquellas del ciclo más bajo o atrasado.
	La matrícula en las asignaturas en riesgo académico y más atrasadas estarán registradas por defecto ya que su matrícula tiene carácter obligatorio; solo se podrá seleccionar la sección.
	
	c. Retiro Parcial: es la prerrogativa de eliminar la matrícula de hasta tres (03) asignaturas, dentro del plazo que vence el último día útil de la quinta semana después del inicio de clases del período académico.
No es posible el retiro parcial de las asignaturas matriculadas en el ciclo más bajo, ni de las desaprobadas por segunda o tercera vez, ni de las que son prerrequisito (en caso se encuentre matriculado en una asignatura y su prerrequisito). 

	d. Retiro Total: es el procedimiento mediante el cual el estudiante solicita a su Decano, la anulación total de su matrícula. Procede sólo por motivos de fuerza mayor y se podrá presentar hasta el último día útil de la penúltima semana de clases.
	No procede un retiro Total cuando el estudiante ha rendido todas las evaluaciones regulares de alguna de las asignaturas en la que se encuentra matriculado o si en los dos ciclos regulares precedentes ha optado por el retiro total o si tiene algún curso desaprobado dos veces o más al periodo académico regular precedente. 

	Los estudiantes que soliciten el retiro total deberán adjuntar la debida documentación que sustente los motivos por  los cuales solita dicha medida.

	e. Retiro Reglamentario: Es el procedimiento de oficio ejecutado por ORCE que elimina la matrícula del estudiante, por contravenir al presente reglamento.
Pudiendo ser: por eliminación de la asignatura-sección, por registro convalidatorio tardío que hace innecesaria una matrícula obligatoria, por no haber aprobado prerrequisito, o por activación irregular del código de alumno separado temporalmente o retirado definitivamente, etc.

	f. Retiro Definitivo: es el procedimiento voluntario o de oficio mediante el cual un estudiante es desvinculado de manera definitiva de la UNI. Procede a solicitud del estudiante ante su Decano o por mandato de Resolución Decana! o Rectoral, motivada por falta disciplinaria muy grave, por Exceso de Licencia o por Bajo Rendimiento Académico, conforme a ley y los reglamentos de la UNI. 

	g. Reserva de Matrícula: es la situación a la que pasa aquel estudiante que ha decidido dejar de estudiar por uno o más periodos académicos (suspensión voluntaria). Ejerce así su derecho de postergar su matrícula. ORCE, al cierre de la Matrícula, la registra de oficio para aquellos estudiantes que no se matricularon. La reserva de matrícula suspende la permanencia y evita la pérdida de su condición de estudiante de la UNI. El período de reserva de matrícula no excederá a los tres (03) años (o seis semestres) académicos consecutivos o alternos (equivalente a 06
periodos académicos). En caso de periodos alternos, el plazo será contabilizado dentro de un lapso que no excederá de cinco (05) años (10 semestres), contados a partir de la primera reserva de matrícula o hacia atrás, desde el momento en que solicita Reincorporación. 

	h. Cambio de Plan de Estudios. A cada estudiante, la Escuela le asigna un Plan de Estudios desde su ingreso, el mismo que puede ser actualizado por el Consejo de Facultad y el Consejo Universitario. No es reversible esta actualización; salvo que no se haya producido matrícula en código exclusivo del nuevo Plan. Cada actualización implica la asimilación de lo cursado y la obligación de cursar (o exoneración) de alguna asignatura perteneciente a ciclos anteriores; según la norma de adaptación propia del nuevo Plan. Estas decisiones del Director de Escuela se registran en el historial de cada alumno y éste debe verificar la idoneidad del registro, antes de la siguiente matrícula.

	i. Tutoría Obligatoria: es la orientación y el acompañamiento en su desarrollo académico a los estudiantes en riesgo académico. Es un requisito para la matrícula de los estudiantes con asignaturas con 2 ó 3 desaprobaciones. Al culminar el semestre el tutor eleva un informe sobre la tutoría y desarrollo académico del estudiante en riesgo académico. 

	j. Oferta de Matrícula: Formato con el listado de asignaturas que cada alumnom encontrará en pantalla, para seleccionar su matrícula. Aplica los prerrequisitos y la dispersión de hasta tres ciclos. Destaca las asignaturas para matrícula obligatoria.

	k. Reporte de Matrícula: es el documento que muestra las asignaturas matriculadas en el período académico vigente, y deberá ser visado por la Oficina de Estadística de la Facultad.

	l. Boleta de Matrícula: es el documento que muestra las asignaturas registradas en la ORCE, luego del Cierre de Matrícula, para el período académico vigente.
Requiere del visado por la Oficina de Estadística de la Facultad.

	m. Turno de Matrícula: es el lapso de apertura digital publicado en el portal web del Sistema de Matrícula UNI y deberá establecer la fecha y horario en que el estudiante realizará su matrícula. Los turnos se organizan según el promedio ponderado de los dos últimos semestres académicos en el que un estudiante presenta matricula regular.

	n. Grupo Cero de matrícula: Es el listado que contiene las matrículas de quienes retornan de Separación Temporal por Bajo Rendimiento Académico y de los alumnos en Riesgo Académico por asignaturas repetidas dos veces. La Comisión de Matrícula cierra el listado producido por la Tutoría, el día anterior a la matricula y lo remite a la ORCE para su registro previo, con mínimo tres horas antes del inicio del primer turno de matrícula.

	o. Asignatura paralela: Este concepto surge durante los procesos de implementación de nuevos planes de estudio. Es la asignatura similar o equivalente del anterior Plan de Estudios que con nuevo código se dicta en el plan vigente. Según la disponibilidad de vacantes o docentes, puede darse con acta paralela en sección única o en sección especial (con docente u horario diferente). La ORCE la instala a pedido expreso de la Facultad, para estudiantes que están por culminar y que conservan el Plan anterior.""",   
    "response":""" Preguntas:
            - ¿Que es la reincorporación?
            - ¿Cual es el plazo limite para la reincorporacion de un estudiante?
            - ¿Si un estudiante reservo su matrícula hace mas de tres (03) años puede realizar la Reincorporación ?
            - ¿Que es un retiro parcial?
            - ¿Que es un retiro total?
            - ¿Hasta cuantas asignaturas pueden eliminarse con un retiro parcial?
            - ¿Hasta cuando se puede eliminar la matrícula de asignaturas conocido como Retiro Parcial?
            - ¿Es posible el retiro parcial de las asignaturas  matriculadas en el ciclo más bajo?
            - ¿Es posible el retiro parcial de las desaprobadas por segunda o tercera vez?
            - ¿Es posible el retiro parcial de las asignaturas que son pre requisito?
            - ¿Se puede solicitar la reincorporaci\u00f3n si se tiene una sanci\u00f3n vigente?
            - ¿Se puede solicitar la reincorporaci\u00f3n ha superado el plazo máximo de Reserva de Matrícula?  
            - ¿Un estudiante puede retirarse de todas las asignaturas matriculadas?
            - ¿De que asignaturas un estudiante no puede retirase?
            - ¿Cuando no procede un retiro total?
            - ¿Que es un retiro definitivo?
            - ¿Que es la Reserva de Matrícula?
            - ¿Si el estudiante ha rendido todas las evaluaciones regulares de alguna de las asignaturas en la que se encuentra matriculado procede el retiro total?
    """,
}]