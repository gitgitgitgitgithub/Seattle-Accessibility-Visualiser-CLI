# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:19:17 2026

@author: coleb
"""


from prompter import request_parser, reminder_dict
from data_loader import load_all_data

def main():
    print("Loading Data...")
    data = load_all_data()
    print("Data Load Successful. Please enter request.")
    print(reminder_dict)
    
    request =""
    while request !="end":
        prompt= input()
        if prompt== "end":
            request = "end"
        elif prompt == "help":
            print(reminder_dict)
        else:
            request = request_parser(prompt,data)
            
            print("Enter request or enter 'end' to end session, or enter 'help' for help")

if __name__ == "__main__":
    main()
