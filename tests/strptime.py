from datetime import datetime
from dateutil.parser import parse

# date_time_str = '18/09/19 01:55:19'


# date_time_obj = datetime.strptime(date_time_str, '%d.%m.%Y').date()
# date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d")


def _vali_date(date_text):
    if date_text:
        try:
            # res = datetime.strptime(date_text, '%d.%m.%Y')
            result = datetime.strptime(date_text, '%d.%m.%Y').date()
        except ValueError:
            # raise ValueError("Incorrect data format, should be YYYY-MM-DD")
            result = None
            # return False
        return result


def _is_valid(self, val):
    result = False
    if (val not in ['', 'Відсутня'] and val is not None):
        # if data is valid date - datetime.strptime(list5[0].strip(), '%d.%m.%Y').date()
        # import datetime
        # datetime.datetime(year=year,month=month,day=day,hour=hour)
        # 
        result = True
    return result


def is_valid_date(date):
    if date:
        try:
            res = parse(date)
            print(res)
            return True
        except ValueError:
            return False
    return False


date_text = '01.01.0000'
# res = is_valid_date(date_text)
res = validate(date_text)
print(res)

# print("The type of the date is now", type(date_time_obj))
# print("The date is", date_time_obj)
