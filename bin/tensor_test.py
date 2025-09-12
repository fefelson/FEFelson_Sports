import pandas as pd
import torch

from fefelson_sports.tensors.baseball.baseball_atomics import (NumBasesIfHit, IsHR, IsHit, HitDistanceSelect, HitAngleSelect, HitStyleSelect, PitchTypeSelect, PitchXSelect, PitchYSelect, PitchVelocitySelect, IsSwing, SwingResult)
from fefelson_sports.tensors.baseball.datasets import (NumBasesIfHitDataset, IsHRDataset, IsHitDataset, HitDistanceDataset, HitAngleDataset, HitStyleDataset, PitchTypeDataset, PitchXDataset, PitchYDataset, PitchVelocityDataset, IsSwingDataset, SwingResultDataset)
from fefelson_sports.tensors.trainer import BinaryTrainer, ClassifyTrainer, RegressionTrainer

from fefelson_sports.database.models.database import get_db_session

PITCH_TYPE_LABELS = ["changeup", "curve", "cutter", "two-seam fb", "fastball", "forkball", "four-seam fb",
                    "sweeper", "splitter", "screwball", "sinker", "slider", "slow curve", "slurve", 
                    "knuckle curve", "knuckleball", "eephus pitch"]


BATTER_QUERY = """SELECT p.batter_id
                    FROM pitches p
                    WHERE p.batter_id IN (
                        SELECT DISTINCT p2.batter_id
                        FROM pitches p2
                        INNER JOIN games g ON p2.game_id = g.game_id
                        WHERE g.season = 2025
                    )
                    GROUP BY p.batter_id
                    HAVING COUNT(p.pitch_id) > 333;      
                """


PITCHER_QUERY = """
                    SELECT p.pitcher_id
                    FROM pitches p
                    WHERE p.pitcher_id IN (
                        SELECT DISTINCT p2.pitcher_id
                        FROM pitches p2
                        INNER JOIN games g ON p2.game_id = g.game_id
                        WHERE g.season = 2025
                    )
                    GROUP BY p.pitcher_id
                    HAVING COUNT(p.pitch_id) > 999;
                    """


STADIUM_QUERY = """SELECT DISTINCT s.stadium_id, s.name
                FROM at_bats AS ab
                INNER JOIN games AS g ON ab.game_id = g.game_id 
                INNER JOIN stadiums AS s on g.stadium_id = s.stadium_id               
                """


def query_db(query):
    
    # print(query)
    with get_db_session() as session:
        df = pd.read_sql(query, session.bind)
    return df


def num_bases():   

    for _, row in query_db(STADIUM_QUERY).iterrows():

        stadiumId = row["stadium_id"]
        print(f"\n\n{row['name']}\n")

        atomicTrainer = ClassifyTrainer(class_labels=["single", "double", "triple", "hr"])
        try:
            atomicTrainer.dojo(NumBasesIfHit(stadiumId=stadiumId), NumBasesIfHitDataset(entityId=stadiumId))
        except ValueError:
            pass


def is_hit():   

    for _, row in query_db(STADIUM_QUERY).iterrows():

        stadiumId = row["stadium_id"]
        print(f"\n\n{row['name']}\n")

        atomicTrainer = BinaryTrainer(class_labels=["out", "hit"])
        try:
            atomicTrainer.dojo(IsHit(stadiumId=stadiumId), IsHitDataset(entityId=stadiumId))
        except ValueError:
            pass


def is_hr():
    
    
    for _, row in query_db(STADIUM_QUERY).iterrows():

        stadiumId = row["stadium_id"]
        print(f"\n\n{row['name']}\n")

        atomicTrainer = BinaryTrainer(class_labels=["weak", "HR"])
        try:
            atomicTrainer.dojo(IsHR(stadiumId=stadiumId), IsHRDataset(entityId=stadiumId))
        except ValueError:
            pass


def is_swing():
    
    atomicTrainer = BinaryTrainer(class_labels=["NO", "YES"])
    for _, row in query_db(BATTER_QUERY).iterrows():
        batterId = row['batter_id']
        try:
            atomicTrainer.dojo(IsSwing(entityId=batterId), IsSwingDataset(entityId=batterId))
        except ValueError:
            pass

def swing_result():
    
    atomicTrainer = ClassifyTrainer(class_labels=["swinging strike", "foul ball", "in play"])
    for _, row in query_db(BATTER_QUERY).iterrows():
        batterId = row['batter_id']
        try:
            atomicTrainer.dojo(SwingResult(entityId=batterId), SwingResultDataset(entityId=batterId))
        except ValueError:
            pass


def hit_distance():
    
    atomicTrainer = RegressionTrainer()
    for _, row in query_db(BATTER_QUERY).iterrows():
        batterId = row['batter_id']
        try:
            atomicTrainer.dojo(HitDistanceSelect(entityId=batterId), HitDistanceDataset(entityId=batterId))
        except ValueError:
            pass


def hit_angle():
    
    atomicTrainer = RegressionTrainer()
    for _, row in query_db(BATTER_QUERY).iterrows():
        batterId = row['batter_id']
        try:
            atomicTrainer.dojo(HitAngleSelect(entityId=batterId), HitAngleDataset(entityId=batterId))
        except ValueError:
            pass



def get_pitcher_class_weights(pitcher_id: int, num_classes: int = 17, smoothing: float = 1e-5) -> torch.Tensor:
    """
    Query pitch type counts for a given pitcher_id and return per-class weights for CrossEntropyLoss.
    Unused pitch types get weight 0.0 (or could use float('inf') if masking).

    Args:
        pitcher_id (int): The pitcher ID.
        num_classes (int): Total number of pitch type classes.
        smoothing (float): Smoothing factor to avoid division by zero.

    Returns:
        torch.Tensor: A tensor of shape (num_classes,) with per-class weights.
    """
    # Query pitch type counts for the pitcher
    query = f"""
        SELECT pitch_type_id, COUNT(*) AS pitch_count
        FROM pitches AS p
        INNER JOIN pitch_types AS pt ON p.pitch_type_name = pt.pitch_type_name
        WHERE pitcher_id = '{pitcher_id}'
        GROUP BY pitch_type_id;
    """
    df = query_db(query)

    # Convert to a dictionary {pitch_type_id: count}
    pitch_counts = dict(zip(df['pitch_type_id'], df['pitch_count']))
    total = sum(pitch_counts.values())

    # Build weights
    weights = []
    for i in range(num_classes):
        count = pitch_counts.get(i, 0)
        if count == 0:
            weights.append(0.0)
        else:
            freq = count / total
            weights.append(1.0 / (freq + smoothing))

    return torch.tensor(weights, dtype=torch.float32)



def pitch_velocity_select():

    # atomicTrainer = RegressionTrainer(n=2)
    # for throws in ("R", "L"):
    #     atomicTrainer.dojo(PitchLocationSelect(entityId=throws), PitchLocationDataset(condition=f"pitcher.throws = '{throws}'"), patience=-1)

    for _, row in query_db(PITCHER_QUERY).iterrows():
        pitcherId = row['pitcher_id']
        atomicTrainer = RegressionTrainer()
        try:
            atomicTrainer.dojo(PitchVelocitySelect(entityId=pitcherId), PitchVelocityDataset(entityId=pitcherId))
        except ValueError:
            pass


def pitch_location_select():

    atomicTrainer = RegressionTrainer(n=2)
    for throws in ("R", "L"):
        atomicTrainer.dojo(PitchLocationSelect(entityId=throws), PitchLocationDataset(condition=f"pitcher.throws = '{throws}'"), patience=-1)

    for _, row in query_db(PITCHER_QUERY).iterrows():
        pitcherId = row['pitcher_id']
        atomicTrainer = RegressionTrainer(n=2)
        try:
            atomicTrainer.dojo(PitchLocationSelect(entityId=pitcherId), PitchLocationDataset(entityId=pitcherId))
        except ValueError:
            pass


def pitch_x_select():
    
    # atomicTrainer = ClassifyTrainer(class_labels=PITCH_TYPE_LABELS, class_weights=class_weights)
    # for throws in ("R", "L"):
    #     atomicTrainer.dojo(PitchTypeSelect(entityId=throws), PitchTypeDataset(condition=f"pitcher.throws = '{throws}'"), patience=2) 

    for _, row in query_db(PITCHER_QUERY).iterrows():
        pitcherId = row['pitcher_id']
        atomicTrainer = RegressionTrainer()
        try:
            atomicTrainer.dojo(PitchXSelect(entityId=pitcherId), PitchXDataset(entityId=pitcherId)) 
        except ValueError:
            pass


def pitch_y_select():
    
    # atomicTrainer = ClassifyTrainer(class_labels=PITCH_TYPE_LABELS, class_weights=class_weights)
    # for throws in ("R", "L"):
    #     atomicTrainer.dojo(PitchTypeSelect(entityId=throws), PitchTypeDataset(condition=f"pitcher.throws = '{throws}'"), patience=2) 

    for _, row in query_db(PITCHER_QUERY).iterrows():
        pitcherId = row['pitcher_id']
        atomicTrainer = RegressionTrainer()
        try:
            atomicTrainer.dojo(PitchYSelect(entityId=pitcherId), PitchYDataset(entityId=pitcherId)) 
        except ValueError:
            pass

def pitch_type_select():

    class_weights = torch.tensor([
    9.109978,        # 0  - changeup
    12.382227,       # 1  - curve
    14.138336,       # 2  - cutter
    61.366463,       # 3  - two-seam fb
    1191.307763,     # 4  - fastball
    3882.472000,     # 5  - forkball
    2.964097,        # 6  - four-seam fb
    53.858144,       # 7  - sweeper
    52.524751,       # 8  - splitter
    15655.129032,    # 9  - screwball
    7.048595,        # 10 - sinker
    5.443751,        # 11 - slider
    6670.914089,     # 12 - slow curve
    769.263325,      # 13 - slurve
    53.957695,       # 14 - knuckle curve
    2648.343793,     # 15 - knuckleball
    2653.774436      # 16 - eephus pitch
], dtype=torch.float32)

    
    # atomicTrainer = ClassifyTrainer(class_labels=PITCH_TYPE_LABELS, class_weights=class_weights)
    # for throws in ("R", "L"):
    #     atomicTrainer.dojo(PitchTypeSelect(entityId=throws), PitchTypeDataset(condition=f"pitcher.throws = '{throws}'"), patience=2) 

    for _, row in query_db(PITCHER_QUERY).iterrows():
        pitcherId = row['pitcher_id']
        pitcher_weights = get_pitcher_class_weights(pitcher_id=pitcherId)
        atomicTrainer = ClassifyTrainer(class_labels=PITCH_TYPE_LABELS, class_weights=pitcher_weights)
        try:
            atomicTrainer.dojo(PitchTypeSelect(entityId=pitcherId), PitchTypeDataset(entityId=pitcherId)) 
        except ValueError:
            pass


if __name__ == "__main__":

    torch.manual_seed(42)
    torch.use_deterministic_algorithms(True)

    # pitch_type_select()
    # pitch_velocity_select()
    # pitch_x_select()
    # pitch_y_select()
    
    # is_swing()
    # swing_result()
    # hit_distance()
    # hit_angle()
    # is_hit()
    # is_hr()
    num_bases()
    
