

def lines_exists_in_log(lines_to_find):
    """
    Returns true if all lines are found within the log.
    :param start: The start time to start searching through the logs.
    :param lines_to_find: A list of lines to search for.
    :return: True if all lines are found, false otherwise.
    """

    with open('Salamandbot2.log') as f:
        lines = f.readlines()

    # this will be the list that tracks remaining lines
    remaining_lines = []

    for line in lines:
        for find_line in lines_to_find:
            if find_line in line and find_line not in remaining_lines:
                remaining_lines.append(find_line)

    if remaining_lines.sort() == lines_to_find.sort():
        return True
    
    return False