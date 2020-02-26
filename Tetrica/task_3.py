import pandas as pd
import numpy as np


def read_lessons(file: str, file_dict=None):
    if file_dict is None:
        file_dict = {'id': [], 'event_id': [], 'subject': [], 'scheduled_time': []}

    with open(file, 'r') as inf:
        for lines_num, lines in enumerate(inf):
            line = lines.split()
            if 1 < lines_num < 378 + 2:
                file_dict['id'] += [line[0]]
                file_dict['event_id'] += [line[2]]
                file_dict['subject'] += [line[4]]
                file_dict['scheduled_time'] += [(line[6] + ' ' + line[7])]
    return pd.DataFrame.from_dict(file_dict)


def read_other(file: str, rows_count: int, file_dict=None):
    if file_dict is None and '/participants' in file:
        file_dict = {'event_id': [], 'user_id': []}
    elif file_dict is None and '/quality' in file:
        file_dict = {'lesson_id': [], 'tech_quality': []}
    elif file_dict is None and '/users' in file:
        file_dict = {'id': [], 'role': []}
    with open(file, 'r') as inf:
        for lines_num, lines in enumerate(inf):
            line = lines.split()
            if 1 < lines_num < rows_count + 2:
                if '/participants' in file:
                    file_dict['event_id'] += [line[0]]
                    file_dict['user_id'] += [line[2]]
                elif '/quality' in file:
                    try:
                        file_dict['lesson_id'] += [line[0]]
                        file_dict['tech_quality'] += [line[2]]
                    except IndexError:
                        file_dict['tech_quality'] += [0]
                elif '/users' in file:
                    file_dict['id'] += [line[0]]
                    file_dict['role'] += [line[2]]
    return pd.DataFrame.from_dict(file_dict)


def phys_gpa(lessons_df: pd.DataFrame, quality_df: pd.DataFrame, average_rating=None):
    """
    Filters the lessons by subject = phys.
    Counts and adds the average rating for them in the DataFrame from the lessons file.
    """
    if average_rating is None:
        average_rating = {}

    phys_lessons = lessons_df.loc[lessons_df['subject'] == 'phys']  # Filter phys lessons
    phys_quality = quality_df.loc[quality_df['lesson_id'].isin(phys_lessons['id'])]  # Filter phys quality
    phys_quality = phys_quality.astype({'lesson_id': object, 'tech_quality': float})  # Change type quality to float
    """ 
    Collect all the grades for the each lesson
    """
    for lesson_id, tech_quality in phys_quality.itertuples(index=False):
        if tech_quality != 0:
            if lesson_id in average_rating:
                average_rating[lesson_id] += [tech_quality]
            else:
                average_rating.setdefault(lesson_id, [tech_quality])
    """
    Find the average rating for the lesson.
    """
    for i in average_rating:
        average_rating[i] = sum(average_rating[i]) / len(average_rating[i])
    """
    Create a DataFrame with id and average_rating columns
    """
    reform_ar = dict.fromkeys(['id'], [*average_rating.keys()])
    reform_ar.update(dict.fromkeys(['average_rating'], [*average_rating.values()]))
    av_df = pd.DataFrame.from_dict(reform_ar)
    """
    Filter phys lessons that have an average rating and add a column with an average rating for them
    """
    phys_lessons = phys_lessons.loc[phys_lessons['id'].isin(av_df['id'])]  # Filter
    phys_lessons = phys_lessons.reset_index(drop=True)  # Drop index count for compare
    phys_lessons['average_rating'] = np.where(
        phys_lessons['id'] == av_df['id'], av_df['average_rating'], '-')  # Compare

    return phys_lessons


def lessons_add_user_id(lessons_df: pd.DataFrame, participants_df: pd.DataFrame, users_df: pd.DataFrame):
    """
    Add to lesson_df (from file lessons.txt) column of user_id, who phys tutor.
    """
    participants_df = participants_df.merge(users_df, left_on='user_id', right_on='id', how='inner')  # Add 'role'
    # from users to participants
    participants_df = participants_df.drop('id', axis='columns')  # Delete 'id' column
    participants_df = participants_df.loc[participants_df['event_id'].isin(lessons_df['event_id'])]  # Filter
    # of participants phys
    participants_df = participants_df.loc[participants_df['role'] == 'tutor']  # Tutor participants filter
    participants_df = participants_df.drop_duplicates()  # Drop duplicates

    lessons_df = lessons_df.merge(participants_df, left_on='event_id', right_on='event_id', how='inner')  # Add
    # 'user_id'
    lessons_df = lessons_df.drop('role', axis='columns')  # Drop 'role' column

    return lessons_df


def tutor_average_rating(lessons_df: pd.DataFrame):
    """
    Calculating the average rating of each tutor by day
    """
    lessons_df['average_rating'] = pd.to_numeric(lessons_df['average_rating'])  # Change type average_rating to float
    lessons_df['scheduled_time'] = pd.to_datetime(lessons_df['scheduled_time'])  # Change type scheduled_time
    # to datetime
    lessons_df = lessons_df.groupby([pd.Grouper(key='scheduled_time', freq='D'), 'user_id']).mean()  # Calculating
    # the average rating of each tutor by day

    return lessons_df


def tutor_rate_lowest(lessons_file: str, participants_file: str, participants_rows: int, users_file: str,
                      users_rows: int, quality_file: str, quality_rows: int):
    """
    ID of teachers with a minimum rating by day
    """
    lessons = read_lessons(lessons_file)
    participants = read_other(participants_file, participants_rows)
    users = read_other(users_file, users_rows)
    quality = read_other(quality_file, quality_rows)

    lessons = phys_gpa(lessons, quality)
    lessons = lessons_add_user_id(lessons, participants, users)
    lessons = tutor_average_rating(lessons)
    lessons = lessons.reset_index()

    return lessons.groupby(['scheduled_time'])['user_id', 'average_rating'].min()


lessons = './tech_quality/lessons.txt'
participants = './tech_quality/participants.txt'
users = './tech_quality/users.txt'
quality = './tech_quality/quality.txt'

print(tutor_rate_lowest(lessons, participants, 743, users, 743, quality, 365))
