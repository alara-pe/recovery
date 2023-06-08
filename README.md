# recovery 

La recolección de evidencias es una parte fundamental en la realización de un forense. Disponer de la información claray organizada es algo que puede facilitar la labor delforense. 
El objetivo de este proyecto es crear un programa que, dado un rango de fechas, sea capaz de extraer diversa información de un sistema Windows como la actividad del usuario, los programas abiertos, el historial de navegación, distinta información del registro de Windows... en dicho rango de tiempo.


Dando un rango de tiempo, se puede extraer información de interés para el forense:
• Fechas de cambio de ramas de registro (CurrentVersionRun)<
• Archivos recientes/n
• Programas instalados
• Programas abiertos
• Historial de navegación
• Dispositivos conectados
• Eventos de log

Tenemos las opciones ¨-i¨ para indicar la fecha en la que queremos empezar la recopilacion de datos y la opcion ¨-f¨ para indicar la checha final, sino indicamos la ficha final el programa actuara hasta la fecha actual, sino indicamos la fecha de inicio el programa actuara desde la fecha actual hasta 4 horas antes. Las fechas se introducen por argumentos.

Para que nuestro programa funcione correctamente tendremos que tener instaladas las siguientes librerias de python : 
-argparse
-winreg
-datetime
-psutil
-win32evtlog
-tempfile
-wmi
-browser-history
Se instalan con el comando ¨pip install argparse¨.

