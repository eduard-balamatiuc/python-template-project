from system.database.database import DataBase

class System:

    def __init__(self) -> None:
        self.allowed_actions = """
            Allowed actions can be found below:
            create buget -n <name> -d <description>
            add money -b <name> -a <amount>
            add expense -b <name> -a <amount> -c <category>
            add budget goal -b <name> -a <amount>
            get stats -b <name>
            save
            help
            exit
        """
        self.system_active = True
        self.database = DataBase(file_path="/Users/eduard.balamatiuc/projects/python-template-project/memory/database_v1.json")
    
    def run(self):
        """
        Main loop for the system.
        """
        while self.system_active:
            user_input = input("Waiting for command (type help if you need some)... ")
            if user_input.startswith("create buget "):
                self.create_buget(user_input)
            elif user_input.startswith("add money "):
                self.add_money(user_input)
            elif user_input.startswith("add expense "):
                self.add_expense(user_input)
            elif user_input.startswith("add budget goal "):
                self.add_budget_goal(user_input)
            elif user_input.startswith("get stats "):
                self.get_stats(user_input)
            elif user_input.startswith("help"):
                print(self.allowed_actions)
            elif user_input.startswith("save"):
                self.database.save_database_state()
            elif user_input.startswith("exit"):
                self.system_active = False
                print("Exiting system...")
            else:
                print("Invalid command, please try again.")
                
    def process_user_input(self, user_input: str, allowed_action: str):
        """
        Process the user_input string and extract the parameters outside of the allowed action
        
        Args:
            user_input (str): The user's input string
            allowed_action (str): The allowed action to be processed
            
        Returns:
            dict: A dictionary containing the extracted parameters
        """
        # Extract the start string which is the allowed action
        start_string = user_input[:len(allowed_action)]
        if start_string != allowed_action:
            raise ValueError(f"Invalid action: {user_input}")
        
        # Extract the parameters from the user_input string
        parameters = user_input[len(allowed_action):]

        # Extract the parameters from the parameters string
        # Example: -n buget_1 -d something_interesting
        # Result: {"-n": "buget_1", "-d": "something_interesting"}
        parameters_dict = {}
        for parameter in parameters.split("-")[1:]:
            parameters_dict[f"-{parameter[0]}"] = parameter[2:-1]

        return parameters_dict
    
    def create_buget(self, user_input: str):
        """This function creates a new buget based on the user_input
        
        Args:
            user_input (str): The user command that was given.
        """
        user_parameters_dict = self.process_user_input(user_input, allowed_action="create buget ")
        self.database.database["budgets"].append(
            {
                "name": user_parameters_dict["-n"],
                "description": user_parameters_dict["-d"],
                "current_amount": 0,
                "action_history": [],
                "goal": None,
            }
        )

    def add_money(self, user_input: str):
        """This function adds money to a specific mentioned buget
        
        Args:
            user_input (str): The user command that was given.
        """
        user_parameters_dict = self.process_user_input(user_input, allowed_action="add money ")
        budget_name_to_update = user_parameters_dict["-b"]
        for budget in self.database.database["budgets"]:
            if budget["name"] == budget_name_to_update:
                budget["current_amount"] += int(user_parameters_dict["-a"])
                budget["action_history"].append(f"+{user_parameters_dict["-a"]}")

    def add_expense(self, user_input: str):
        """This function adds expenses to a specific mentioned buget
        
        Args:
            user_input (str): The user command that was given.
        """
        user_parameters_dict = self.process_user_input(user_input, allowed_action="add expense ")
        budget_name_to_update = user_parameters_dict["-b"]
        for budget in self.database.database["budgets"]:
            if budget["name"] == budget_name_to_update:
                budget["current_amount"] -= int(user_parameters_dict["-a"])
                budget["action_history"].append(f"-{user_parameters_dict["-a"]} for {user_parameters_dict["-c"]}")

    def add_budget_goal(self, user_input: str):
        """This function adds expenses to a specific mentioned buget
        
        Args:
            user_input (str): The user command that was given.
        """
        user_parameters_dict = self.process_user_input(user_input, allowed_action="add budget goal ")
        budget_name_to_update = user_parameters_dict["-b"]
        for budget in self.database.database["budgets"]:
            if budget["name"] == budget_name_to_update:
                budget["goal"] = int(user_parameters_dict["-a"])

    def get_stats(self, user_input: str):
        """This function adds expenses to a specific mentioned buget
        
        Args:
            user_input (str): The user command that was given.
        """
        user_parameters_dict = self.process_user_input(user_input, allowed_action="get stats ")
        budget_name_to_update = user_parameters_dict["-b"]
        for budget in self.database.database["budgets"]:
            if budget["name"] == budget_name_to_update:
                if budget["goal"] is None:
                    print("You did not set any budget goal yet")
                else:
                    print(f"You achieved {(budget["current_amount"]*100)/budget["goal"]}")
