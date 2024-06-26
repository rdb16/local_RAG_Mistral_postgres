from datetime import datetime
import pytz


def parse(pdf_date_string):
    try:
        if pdf_date_string.startswith("D:"):
            pdf_date_string = pdf_date_string[2:]

        datetime_part = pdf_date_string[:14]
        timezone_part = pdf_date_string[15:]
        # print("datetime_part: ", datetime_part, ", timezone_part: ", timezone_part)

        # Parse datetime_part
        naive_date = datetime.strptime(datetime_part, "%Y%m%d%H%M%S")
        # print("naive_date: ", naive_date)

        # Parse timezone offset
        sign = -1 if timezone_part[0] == '-' else 1
        hours_offset = int(timezone_part[0:2])
        # print("hours_offset: ", hours_offset)
        minutes_offset = int(timezone_part[4:6].replace("'", ""))
        # print("minutes_offset: ", minutes_offset)

        # # Vérifiez que l'offset est dans une plage valide
        # if abs(hours_offset) > 14 or abs(minutes_offset) > 59:
        #     raise ValueError(f"Invalid timezone offset: {hours_offset} hours, {minutes_offset} minutes")

        # Calcul de l'offset total en minutes
        total_minutes = sign * (hours_offset * 60 + minutes_offset)
        # print("total_minutes: ", total_minutes)

        # Créer la timezone
        timezone = pytz.FixedOffset(total_minutes)
        # print("timezone: ", timezone)
        # Parser la date et l'heure sans l'offset
        # Appliquer la timezone
        local_date = naive_date.replace(tzinfo=timezone)
        return local_date.isoformat()
    except Exception as e:
        print(f"Error parsing PDF date: {e}")
        return None


def main():
    # Exemple d'utilisation
    pdf_date = "D:20070503123810-04'00'"
    formatted_date = parse(pdf_date)
    print(formatted_date)


if __name__ == "__main__":
    main()
