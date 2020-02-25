import pandas as pd
import numpy as np

pd.set_option('max_rows', 800)
pd.set_option('max_columns', 10)
pd.set_option('expand_frame_repr', False)


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


lessons = read_lessons('./tech_quality/lessons.txt')
participants = read_other('./tech_quality/participants.txt', 743)
users = read_other('./tech_quality/users.txt', 743)
quality = read_other('./tech_quality/quality.txt', 365)

lessons = phys_gpa(lessons, quality)

participants = participants.merge(users, left_on='user_id', right_on='id', how='inner')  # Add 'role'
# from users to participants
participants = participants.drop('id', axis='columns')  # Delete 'id' column
participants = participants.loc[participants['event_id'].isin(lessons['event_id'])]  # Filter of participants phys
participants = participants.loc[participants['role'] == 'tutor']  # Filter of participants
participants = participants.drop_duplicates()  # Drop duplicates

lessons = lessons.merge(participants, left_on='event_id', right_on='event_id', how='inner')  # Add 'user_id'
lessons = lessons.drop('role', axis='columns')  # Drop 'role' column

lessons['average_rating'] = pd.to_numeric(lessons['average_rating'])
lessons['scheduled_time'] = pd.to_datetime(lessons['scheduled_time'])


df = lessons.groupby([pd.Grouper(key='scheduled_time', freq='D'), 'user_id']).mean()
df = df.reset_index()

print(df.groupby(['scheduled_time'])['user_id', 'average_rating'].min())
