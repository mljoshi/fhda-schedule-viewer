import requests
import time
import sys
from send_email import send_message
from da_schedule_viewer import automatic_term_code_and_file_name
from da_schedule_viewer import campus_num_to_campus
# ADD CHECK FOR VALID CRN
# Example input: py waitlist_slot_open.py 3334445555 verizon 01791 01792
# py waitlist_slot_open.py phone_number carrier crn1 crn2 crn3 crn4...
# Add separate functionality of checking for when Staff is replaced by an actual professor

def get_html_text():
    url = "https://ssb-prod.ec.fhda.edu/PROD/fhda_opencourses.P_GetCourseList"
    # FH/DA campus (1/2)
    campus_num = 2
    data = {"termcode":automatic_term_code_and_file_name(campus_num_to_campus(campus_num))[0]}
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"}
    response = requests.post(url, data=data,headers=headers)
    # debugging
    """
    with open("curr_schedule.html","w+") as f:
        f.write(response.text)
    """
    # print(response.status_code, response.text, sep='\n')
    return response.text

# This function assumes that there is at least one number and only gets the first number in the string
def get_num(line):
    for i in range(len(line)):
        if line[i].isdigit():
            initial_ind = i
            break
    for i in range(initial_ind, len(line)):
        if line[i].isdigit():
            final_ind = i
        else:
            break
    return int(line[initial_ind:final_ind + 1])

def get_real_prof(html_text, curr_crn):
    crn_ind = html_text.find(curr_crn)
    # Implement error checking here (or ideally before inputted into this function), the crn is not found when crn_ind == -1
    print("Crn index: ", crn_ind)
    curr_html = html_text[crn_ind + 5::] # Crn is length 5 always
    for i in range(10): # 10 lines before professor info after the crn
        newline_ind = curr_html.find("\n")
        curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    prof_line = curr_html[:next_newline_ind]
    curr_html = curr_html[next_newline_ind + 1::] # Move on to next line, newline is length 1
    
    next_newline_ind = curr_html.find("\n")
    open_slots = get_num(curr_html[:next_newline_ind])
    newline_ind = next_newline_ind
    curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    waitlist_slots = get_num(curr_html[:next_newline_ind])
    newline_ind = next_newline_ind
    curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    waitlist_capacity = get_num(curr_html[:next_newline_ind])

    return ("a href" in prof_line, prof_line[4:-5], open_slots, waitlist_slots, waitlist_capacity) # Consider changing a href logic as if a professor does not have a linked email it would not work (though I'm not sure if this is possible)

def get_slots(html_text, curr_crn):
    crn_ind = html_text.find(curr_crn)
    # Implement error checking here (or ideally before inputted into this function), the crn is not found when crn_ind == -1
    # print("Crn index: ", crn_ind)
    curr_html = html_text[crn_ind + 5::] # Crn is length 5 always
    for i in range(11): # 11 lines before the useful info after the crn
        newline_ind = curr_html.find("\n")
        curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    open_slots = get_num(curr_html[:next_newline_ind])
    newline_ind = next_newline_ind
    curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    waitlist_slots = get_num(curr_html[:next_newline_ind])
    newline_ind = next_newline_ind
    curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    waitlist_capacity = get_num(curr_html[:next_newline_ind])

    return (open_slots, waitlist_slots, waitlist_capacity)

if __name__ == "__main__":
    # crns = ["01791", "01792", "38519"]
    crns = sys.argv[3:]
    # phone_number = "4086053700"
    phone_number = sys.argv[1]
    # carrier = "verizon"
    carrier = sys.argv[2]
    time_sleep_min = 2.5
    time_sleep_sec = time_sleep_min * 60
    real_prof_data = (False, "")
    while(True):
        html_text = get_html_text()
        for i in range(len(crns)):
            curr_crn = crns[i]
            print("Current crn:", curr_crn)
            real_prof_data = get_real_prof(html_text, curr_crn)
            if real_prof_data[0]:
                print("NO LONGER M. STAFF")
                send_message(phone_number, carrier, "\nNO LONGER M. STAFF: " + curr_crn + "\nProf line: " + real_prof_data[1] + "\nOpen slots: " + real_prof_data[2] + "\nWaitlist slots: " + real_prof_data[3] + "\nWaitlist capacity: " + real_prof_data[4]) # \n removes the X-CMAE-Envelope message
                found_prof = True
        print("Sleeping")
        if (real_prof_data[0]):
            print("FOUND PROF:", real_prof_data[1], "\nOpen slots:", real_prof_data[2], "\nWaitlist slots:", real_prof_data[3], "\nWaitlist capacity:", real_prof_data[4])
            found_prof = False
            # Include if don't want to spam
            exit()
        else:
            print("Still M. Staff:", real_prof_data[1], "\nOpen slots:", real_prof_data[2], "\nWaitlist slots:", real_prof_data[3], "\nWaitlist capacity:", real_prof_data[4])
        time.sleep(time_sleep_sec)