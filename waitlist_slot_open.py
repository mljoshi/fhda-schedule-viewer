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

def get_slots(html_text, curr_crn):
    crn_ind = html_text.find(curr_crn)
    # Implement error checking here (or ideally before inputted into this function), the crn is not found when crn_ind == -1
    print("Crn index: ", crn_ind)
    curr_html = html_text[crn_ind + 5::] # Crn is length 5 always
    for i in range(11): # 11 lines before the useful info after the crn
        newline_ind = curr_html.find("\n")
        print("newline_ind: ", newline_ind)
        curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    open_slots = get_num(curr_html[:next_newline_ind])
    print("Open slots: ", open_slots)
    newline_ind = next_newline_ind
    print("newline_ind: ", newline_ind)
    curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    waitlist_slots = get_num(curr_html[:next_newline_ind])
    print("Waitlist slots: ", waitlist_slots)
    newline_ind = next_newline_ind
    print("newline_ind: ", newline_ind)
    curr_html = curr_html[newline_ind + 1::] # Move on to next line, newline is length 1
    # Get the next newline ind to find where this line ends
    next_newline_ind = curr_html.find("\n")
    waitlist_capacity = get_num(curr_html[:next_newline_ind])
    print("Waitlist capacity: ", waitlist_capacity)

    return (open_slots, waitlist_slots, waitlist_capacity)

if __name__ == "__main__":
    crns = sys.argv[3:]
    phone_number = sys.argv[1]
    carrier = sys.argv[2]
    time_sleep_min = 2.5
    time_sleep_sec = time_sleep_min * 60
    found_waitlist_slots = False
    found_open_slots = False
    while(True):
        html_text = get_html_text()
        for i in range(len(crns)):
            curr_crn = crns[i]
            print("Current crn:", curr_crn)
            (open_slots, waitlist_slots, waitlist_capacity) = get_slots(html_text, curr_crn)
            if (waitlist_slots > 0):
                print("WAITLIST SLOT(s) AVAILABLE")
                send_message(phone_number, carrier, "\nWAITLIST SLOT(s) AVAILABLE. CRN: " + curr_crn) # \n removes the X-CMAE-Envelope message
                found_waitlist_slots = True
            # send_message(phone_number, carrier, "test123 " + curr_crn)
            if ((waitlist_slots == waitlist_capacity) and (open_slots > 0)):
                print("OPEN SLOT(s) AVAILABLE")
                send_message(phone_number, carrier, "\nOPEN SLOT(s) AVAILABLE. CRN: " + curr_crn) # \n removes the X-CMAE-Envelope message
                found_open_slots = True
        print("Sleeping")
        if (found_waitlist_slots):
            print("FOUND WAITLIST SLOTS SOMEWHERE")
            found_waitlist_slots = False
        else:
            print("No available waitlist slots found")
        if (found_open_slots):
            print("FOUND OPEN SLOTS SOMEWHERE")
            found_open_slots = False
        else:
            print("No available open slots found")
        time.sleep(time_sleep_sec)