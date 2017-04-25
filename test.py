with open("scripts/machine_learning/trained_naive_bayes_model/user_tags_v4", "r") as f:
    with open ("scripts/data_retrieval/all_users_info", "r") as f2:
        lines = f.readlines()
        tagged_users = set()
        for line in lines:
            tagged_users.add(line[:line.find(":")])
        lines = f2.readlines()
        all_current_users = set()
        for line in lines:
            all_current_users.add(line.split(",")[1])
        for user in tagged_users:
            if user not in all_current_users:
                print user        
