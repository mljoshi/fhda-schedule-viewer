import requests
import datetime
import os.path

def quarter_num_to_quarter(quarter_num):
    if quarter_num == 2:
        return "Fall"
    elif quarter_num == 3:
        return "Winter"
    elif quarter_num == 4:
        return "Spring"
    return "Summer"

def campus_num_to_campus(campus_num):
    if campus_num == 2:
        return "DA"
    return "FH"

def automatic_term_code_and_file_name(campus_name):
    """
    campus_num == 1 for FH, 2 for DA (assumes proper input)
    Date cutoffs (all of them are inclusive for endpoints, making guesses based off 1-14-2024's Academic Calendar for De Anza):
    between 7/8 and 10/15 for Fall
    between 10/16 and 1/31 for Winter
    between 2/1 and 4/23 for Spring
    between 4/24 and 7/7 for Summer
    Making the assumption that summer 2023 is considered a 2024 end school year (i.e. it is a part of the 2023-2024 school year)
    because it has a quarter_num of 1
    """
    if campus_name.lower() == "fh":
        campus_num = 1
    else:
        campus_num = 2
    date_today = datetime.date.today()
    fall_cutoff = datetime.date(date_today.year, 10, 15)
    winter_cutoff = datetime.date(date_today.year, 1, 31)
    spring_cutoff = datetime.date(date_today.year, 4, 23)
    summer_cutoff = datetime.date(date_today.year, 7, 7)
    year = date_today.year
    if date_today <= winter_cutoff: # Winter
        quarter_num = 3
    elif date_today <= spring_cutoff: # Spring
        quarter_num = 4
    elif date_today <= summer_cutoff: # Summer
        quarter_num = 1
    elif date_today <= fall_cutoff: # Fall
        quarter_num = 2
    else: # Winter (past fall cutoff but not accounted for by winter cutoff)
        quarter_num = 3
        year += 1 # Need to add one (for file name purposes) because you may fetch data for Winter 2024 in December 2023 for example
    end_school_year = date_today.year
    if quarter_num == 1 or quarter_num == 2: # Fall and I believe summer as well are considered apart of the next school year (i.e. Fall 2023 is considered Fall 2023-2024 which means the year code is 2024)
        end_school_year += 1
    # 2024 is ending year of the current school year (Ex Fall 2023 is of the 2023-2024 school year, so it's 2024), 10s place is quarter/season (with 2 being fall), 1s place is FH/DA campus (1/2)
    term_code = str(end_school_year) + str(quarter_num) + str(campus_num)
    file_name = campus_num_to_campus(campus_num) + quarter_num_to_quarter(quarter_num) + str(year) + "_" + str(date_today) + ".html"
    return term_code, file_name

def input_to_term_code_and_file_name(campus_name, quarter, year):
    if campus_name.lower() == "fh":
        campus_num = 1
    else:
        campus_num = 2
    if quarter.lower() == "summer":
        quarter_num = 1
    elif quarter.lower() == "fall":
        quarter_num = 2
    elif quarter.lower() == "winter":
        quarter_num = 3
    else:
        quarter_num = 4
    if quarter_num < 3:
        end_school_year = year + 1
    else:
        end_school_year = year
    term_code = str(end_school_year) + str(quarter_num) + str(campus_num)
    date_today = datetime.date.today()
    file_name = campus_num_to_campus(campus_num) + quarter_num_to_quarter(quarter_num) + str(year) + "_" + str(date_today) + ".html"
    return term_code, file_name

if __name__ == "__main__":
    save_path = os.path.dirname(os.path.realpath(__file__)) # Automatically saves to the folder of this script, replace file path as needed
    url = "https://ssb-prod.ec.fhda.edu/PROD/fhda_opencourses.P_GetCourseList"
    campus_name = input("Name of campus (FH/DA)? ")
    automatic_fetch = input("Automatically fetch quarter (Y/N)? ")
    if automatic_fetch.lower() == "y":
        term_code, file_name = automatic_term_code_and_file_name(campus_name)
    else:
        quarter = input("Enter quarter (Summer/Fall/Winter/Spring): ")
        year = int(input("Enter year: "))
        term_code, file_name = input_to_term_code_and_file_name(campus_name, quarter, year)
    complete_file_name = os.path.join(save_path, file_name)
    data = {"termcode":term_code}
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"}
    response = requests.post(url, data=data,headers=headers)
    with open(complete_file_name,"w+") as f:
        f.write(response.text)
    print(response.status_code, response.text, sep='\n')