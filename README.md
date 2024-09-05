# fhda-schedule-viewer

Obtain the html code for Foothill or De Anza College's class schedule (to save for reference or to periodically check for updates on a certain class's registration status)

Automatically saves to the folder that the script is placed in

Waitlist Slot Finder checks every 2.5 min if a waitlist slot has opened in a class with a given crn list

Waitlist Slot Finder usage:

py waitlist_slot_open.py phone_number carrier crn

Example:

py waitlist_slot_open.py 1234567890 verizon 27516

M Staff Finder checks every 2.5 min if a class's professor has changed from M Staff to a real one

M Staff Finder usage:

py m_staff_finder.py phone_number carrier crn

Example:

py m_staff_finder.py 1234567890 verizon 27516

This requires carrier information since it will use an email to send a text message (e.g. Verizon phone's can be texted by emailing 1234567890@vtext.com)
