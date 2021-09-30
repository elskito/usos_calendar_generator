import jinja2
import json
from datetime import datetime
import typer


app = typer.Typer()

class CalendarParser:
    def __init__(self, terminy, przedmioty, lokalizacje, prowadzacy, **kwargs) -> None:
        self.subjects = przedmioty
        self.lecturers = prowadzacy
        self.rooms = lokalizacje
        self.list_of_subjects = self._zip_all_subjects_to_list(terminy)

    def _zip_all_subjects_to_list(self, list_of_subject: list) -> dict:
        len_of_subjects = len(list_of_subject)
        list_of_dicts = []
        for i in range(len_of_subjects):
            if list_of_subject[i]['elementy']:
                list_of_dicts += list_of_subject[i]['elementy']
        return list_of_dicts

    def _change_time_to_ics_format(self, date: str) -> str:
        date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        ics_format = date_time_obj.strftime('%Y%m%dT%H%M%S')
        return ics_format

    def find_subject(self, plan_number: str):
        for item in self.subjects:
            if item['id_pozycjiplanu'] == str(plan_number):
                return f"{item['typzajec']} {item['przedmiot']}"

    def find_lecturer(self, lecturer_id: str):
        for item in self.lecturers:
            if item['id_prowadzacego'] == str(lecturer_id):
                return f"{item['tytulnaukowy']} {item['imie']} {item['nazwisko']}"

    def find_place(self, id_sali: str):
        for item in self.rooms:
            if item['id_sali'] == str(id_sali):
                return f"Budynek: {item['budynek']}, s.{item['sala']}"

    def prepare_for_jinja(self):
        list_for_jinja = []
        i = 10
        for data in self.list_of_subjects:
            tmp = {}
            for key in data:
                if key in ['hdo', 'hod']:
                    tmp[key] = self._change_time_to_ics_format(data[key])
                if key == 'id_pozycjiplanu':
                    tmp[key] = self.find_subject(data[key])
                if key == "id_prowadzacego":
                    tmp[key] = self.find_lecturer(data[key])
                if key == "id_sali":
                    tmp[key] = self.find_place(data[key])
                tmp['uid'] = i
            list_for_jinja.append(tmp)
            i += 1
        return list_for_jinja

@app.command()
def generate(filename: str, template = "rozklad_template.ics"):
    with open(f"{filename}") as file:
        data = json.load(file)

    cp = CalendarParser(**data)

    with open(template) as file_:
        template = jinja2.Template(file_.read())
    
    with open(f'{filename}.ics', 'w') as the_file:
        the_file.write(template.render(dates=cp.prepare_for_jinja()))


if __name__ == "__main__":
    app()
