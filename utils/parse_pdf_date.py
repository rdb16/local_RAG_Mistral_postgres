import datetime
import pytz


def parse(pdf_date):
    # Supprimer le préfixe 'D:' et le dernier groupe de caractères lié au fuseau horaire
    clean_date = pdf_date[2:-7]
    # Convertir la date en objet datetime
    date_format = '%Y%m%d%H%M%S'
    datetime_obj = datetime.datetime.strptime(clean_date, date_format)

    # Extraction et traitement du fuseau horaire
    timezone_info = pdf_date[-6:].replace("'", "")  # par exemple, +02'00' devient +0200
    sign = timezone_info[0]
    hours_offset = int(timezone_info[1:3])
    minutes_offset = int(timezone_info[3:])

    # Créer l'objet timezone
    if sign == '+':
        timezone = pytz.FixedOffset(hours_offset * 60 + minutes_offset)
    else:
        timezone = pytz.FixedOffset(-(hours_offset * 60 + minutes_offset))

    # Associer le fuseau horaire à l'objet datetime
    datetime_obj = timezone.localize(datetime_obj)

    # Convertir l'objet datetime en UTC si nécessaire
    datetime_obj = datetime_obj.astimezone(pytz.utc)

    return datetime_obj.isoformat()


def main():
    # Exemple d'utilisation
    pdf_date = "D:20240417104648+02'00'"
    formatted_date = parse(pdf_date)
    print(formatted_date)


if __name__ == "__main__":
    main()
