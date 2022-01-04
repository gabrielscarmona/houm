# houm

Sistema para realizar seguimiento del recorrido de houmers por las propiedades de Houm.

## Requisitos

Tener instalado docker para realizar las pruebas.

## Instalación

```sh
docker-compose build
docker-compose run web python manage.py migrate
docker-compose run web python manage.py loaddata fixtures/*
docker-compose run web python manage.py test
docker-compose up
docker-compose down
```

### Problema

* Permita que la aplicación móvil mande las coordenadas del Houmer
* Para un día retorne todas las coordenadas de las propiedades que visitó y cuanto tiempo se quedó en cada una
* Para un día retorne todos los momentos en que el houmer se trasladó con una velocidad superior a cierto parámetro

### Solución

Se define almacenar las coordenadas de los houmers en una base postgres la cual tiene soporte
para GIS, que permitirá luego realizar consultas geográficas sobre estos.

Al momento de recibir una posicion se enviaran a una cola de ejecucion de celery para
ser procesada por la tarea de tracking.

Dicha tarea guardará las coordenas junto con el momento de la creacion. Además en base a la
registro de seguimiento anterior se calculará la velocidad y duracion de permanencia en una zona 
cercana a alguna propiedad de houm. Dicha cercanía se determina por un radio de 50mts respecto
a la localizacion de la propiedad.

Por ultimo se exponen recursos en API REST para determinar el tiempo de permanencia en zona de una propiedad.
Y momentos con desplazamientos de velocidad superiores al parametro dado.

### Ejemplo de uso

```sh
# genera un token para usar la api con las credenciales del usuario creado anteriormente
$ curl --location --request POST 'http://127.0.0.1:8000/api/token/' \
--header 'Content-Type: application/json' \
--data-raw '{"username": "houmer1", "password": "houmer1"}'

{"refresh":"<REFRESH_TOKEN>","access":"<TOKEN>"}


# Guarda una posicion
$ curl --location --request POST 'http://127.0.0.1:8000/api/tracking/' \
--header 'Authorization: Bearer <TOKEN>' --data-raw '{"lat": -34.59230, "lng":-58.425789}'

HTTP/1.1 200 OK

# Lista el total de permanencia y la position de la propiedad de Houm del houmer con ID = 2 del dia 03-01-2022
$ curl --location --request GET 'http://127.0.0.1:8000/api/houmer/2/attendance/?date=03-01-2022' \
--header 'Authorization: Bearer <TOKEN>' --header 'Content-Type: application/json' 

[
    {
        "total_duration": 326,
        "geom": "SRID=4326;POINT (-58.4256879365174 -34.5923050897605)"
    },
    {
        "total_duration": 0,
        "geom": "SRID=4326;POINT (-58.4259820523858 -34.581377735346)"
    }
]

# Lista cada momento que el houmer supero los 10km/h el dia 03-01-2022
$ curl --location --request GET 'http://127.0.0.1:8000/api/houmer/2/speed/?date=03-01-2022&min_speed=10' \
--header 'Authorization: Bearer <TOKEN>'

{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 234,
            "created": "2022-01-03T22:21:27.874000Z",
            "speed": 15452
        },
        {
            "id": 231,
            "created": "2022-01-03T21:47:05.198000Z",
            "speed": 5306752
        },
        {
            "id": 190,
            "created": "2022-01-03T18:06:44.879000Z",
            "speed": 1304
        },
        {
            "id": 186,
            "created": "2022-01-03T18:05:49.989000Z",
            "speed": 3193
        },
....        
```
