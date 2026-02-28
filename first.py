tasks = []

def addtask():
    task = input("Please enter a task: ")
    tasks.append(task)
    print(f"Task '{task}' has been added to the list.")

def listtask():
    if not tasks:
        print("There are no tasks... add one!")
    else:
        print("Current tasks: ")
        for index, task in enumerate(tasks):
            print(f"{index}. {task}")

def deleteTask():
    listTasks()
    try:
        tasktoDelete = int(input("Enter the # to delete: "))
        if tasktoDelete >= 0 and tasktoDelete < len(tasks):
            tasks.pop(tasktoDelete)
            print(f"task {tasktoDelete} has been removed.")
        else:
            print(f"Task # to delete ")
    except: 
        print("Invalid Input.")GREEN = "\033[92m"
    RESET = "\033[0m"
    print(f"{GREEN}✓ Task completed{RESET}")


if __name__ == "__main__":
    ### Create a loop to run the app
    print("Welcome to the to-do list!")

    while True:
        print("\n")
        print("Please select one of the following options. ")
        print("----------------------------------------------")
        print("1. Add a new task")
        print("2. Delete a task")
        print("3. List tasks")
        print("4. Quit")

        choice = input("Enter your choice: ")

        if(choice == "1"):
            addtask()
        elif(choice == "2"):
            deletetask()
        elif(choice == "3"):
            listtask()
        elif(choice == "4"):
            break
        else:
            print("Invalid input. Please select 1-4")

            print("Goodbye!")




