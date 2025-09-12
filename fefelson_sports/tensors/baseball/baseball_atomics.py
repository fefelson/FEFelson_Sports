import torch
import torch.nn as nn 

from ..core import BaseModel, ContinuousEmbed, CustomDataset


######################################################################
######################################################################


PITCH_TYPES =17
PITCH_RESULT_TYPES =6

HIT_HARDNESSES =4
HIT_STYLES =6


######################################################################
######################################################################


class PitchTypeSelect(BaseModel):

    _entityType = "pitchers" 
    _leagueId = "mlb"
    _modelName = "pitch_type_select"
    _PITCHER_EM_DIM = 10
    _COUNT_EM_DIM = 6
    _HIDDEN_DIM = 50
    _OUTPUT_DIM = PITCH_TYPES


    def __init__(self, *, entityId, defaultId=None):
        super().__init__(entityId=entityId, defaultId=defaultId)

        self.pitcher_exp = ContinuousEmbed(1, self._PITCHER_EM_DIM)
        self.batter_faces_break = nn.Embedding(2, self._PITCHER_EM_DIM)

        self.balls =  nn.Embedding(4, self._COUNT_EM_DIM)
        self.strikes =  nn.Embedding(3, self._COUNT_EM_DIM)
        self.sequence = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_count = ContinuousEmbed(1, self._COUNT_EM_DIM)

        # Shared layers
        self.shared = nn.Sequential(
            nn.Linear(self._PITCHER_EM_DIM*2+self._COUNT_EM_DIM*4, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._OUTPUT_DIM)
        )
        
        self._load() 


    def forward(self, features):

        # Example: Get embeddings (2D tensors, e.g., [batch_size, embedding_dim])
        pitcher_exp = self.pitcher_exp(features["pitcher_exp"].unsqueeze(1)) 
        batter_faces_break = self.batter_faces_break(features["batter_faces_break"]) 
       
        balls = self.balls(features["balls"])          # [batch_size, embedding_dim]
        strikes = self.strikes(features["strikes"])
        sequence = self.sequence(features["sequence"].unsqueeze(1))
        pitch_count = self.pitch_count(features["pitch_count"].unsqueeze(1))


        x = torch.cat([
            pitcher_exp,
            batter_faces_break,

            balls,
            strikes,
            sequence,
            pitch_count
        ], dim=1)  # [batch_size, total_features] 

        return self.shared(x)
######################################################################
######################################################################


class PitchXSelect(BaseModel):

    _entityType = "pitchers" 
    _leagueId = "mlb"
    _modelName = "pitch_x_select"
    _PITCHER_EM_DIM = 6
    _COUNT_EM_DIM = 6
    _PITCH_TYPE_EM_DIM = 6
    _HIDDEN_DIM = 36
    _OUTPUT_DIM = 1


    def __init__(self, *, entityId, defaultId=None):
        super().__init__(entityId=entityId, defaultId=defaultId)

        self.pitcher_exp = ContinuousEmbed(1, self._PITCHER_EM_DIM)
        self.batter_faces_break = nn.Embedding(2, self._PITCHER_EM_DIM)

        self.balls =  nn.Embedding(4, self._COUNT_EM_DIM)
        self.strikes =  nn.Embedding(3, self._COUNT_EM_DIM)
        self.sequence = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_count = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_type = nn.Embedding(PITCH_TYPES, self._PITCH_TYPE_EM_DIM)

        

        # Shared layers
        self.shared = nn.Sequential(
            nn.Linear(self._PITCHER_EM_DIM*2+self._COUNT_EM_DIM*4+self._PITCH_TYPE_EM_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._OUTPUT_DIM)
        )
        
        self._load() 


    def forward(self, features):

        # Example: Get embeddings (2D tensors, e.g., [batch_size, embedding_dim])
        pitcher_exp = self.pitcher_exp(features["pitcher_exp"].unsqueeze(1)) 
        batter_faces_break = self.batter_faces_break(features["batter_faces_break"]) 
       
        balls = self.balls(features["balls"])          # [batch_size, embedding_dim]
        strikes = self.strikes(features["strikes"])
        sequence = self.sequence(features["sequence"].unsqueeze(1))
        pitch_count = self.pitch_count(features["pitch_count"].unsqueeze(1))
        pitch_type = self.pitch_type(features["pitch_type_id"])


        x = torch.cat([
            pitcher_exp,
            batter_faces_break,

            balls,
            strikes,
            sequence,
            pitch_count,
            pitch_type
        ], dim=1)  # [batch_size, total_features] 

        return self.shared(x)

######################################################################
######################################################################


class PitchYSelect(BaseModel):

    _entityType = "pitchers" 
    _leagueId = "mlb"
    _modelName = "pitch_y_select"
    _PITCHER_EM_DIM = 6
    _COUNT_EM_DIM = 6
    _PITCH_TYPE_EM_DIM = 6
    _HIDDEN_DIM = 36
    _OUTPUT_DIM = 1


    def __init__(self, *, entityId, defaultId=None):
        super().__init__(entityId=entityId, defaultId=defaultId)

        self.pitcher_exp = ContinuousEmbed(1, self._PITCHER_EM_DIM)
        self.batter_faces_break = nn.Embedding(2, self._PITCHER_EM_DIM)

        self.balls =  nn.Embedding(4, self._COUNT_EM_DIM)
        self.strikes =  nn.Embedding(3, self._COUNT_EM_DIM)
        self.sequence = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_count = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_type = nn.Embedding(PITCH_TYPES, self._PITCH_TYPE_EM_DIM)

        

        # Shared layers
        self.shared = nn.Sequential(
            nn.Linear(self._PITCHER_EM_DIM*2+self._COUNT_EM_DIM*4+self._PITCH_TYPE_EM_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._OUTPUT_DIM)
        )
        
        self._load() 


    def forward(self, features):

        # Example: Get embeddings (2D tensors, e.g., [batch_size, embedding_dim])
        pitcher_exp = self.pitcher_exp(features["pitcher_exp"].unsqueeze(1)) 
        batter_faces_break = self.batter_faces_break(features["batter_faces_break"]) 
       
        balls = self.balls(features["balls"])          # [batch_size, embedding_dim]
        strikes = self.strikes(features["strikes"])
        sequence = self.sequence(features["sequence"].unsqueeze(1))
        pitch_count = self.pitch_count(features["pitch_count"].unsqueeze(1))
        pitch_type = self.pitch_type(features["pitch_type_id"])


        x = torch.cat([
            pitcher_exp,
            batter_faces_break,

            balls,
            strikes,
            sequence,
            pitch_count,
            pitch_type
        ], dim=1)  # [batch_size, total_features] 

        return self.shared(x)


######################################################################
######################################################################



class PitchVelocitySelect(BaseModel):

    _entityType = "pitchers" 
    _leagueId = "mlb"
    _modelName = "pitch_velocity_select"
    _PITCHER_EM_DIM = 10
    _PITCH_TYPE_EM_DIM = 10
    _COUNT_EM_DIM = 10
    _HIDDEN_DIM = 72
    _OUTPUT_DIM = 1


    def __init__(self, *, entityId, defaultId=None):
        super().__init__(entityId=entityId, defaultId=defaultId)

        self.pitcher_age = ContinuousEmbed(1, self._PITCHER_EM_DIM)
        self.batter_faces_break = nn.Embedding(2, self._PITCHER_EM_DIM)

        self.balls =  nn.Embedding(4, self._COUNT_EM_DIM)
        self.strikes =  nn.Embedding(3, self._COUNT_EM_DIM)
        self.sequence = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_count = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_type = nn.Embedding(PITCH_TYPES, self._PITCH_TYPE_EM_DIM)
        self.pitch_x = ContinuousEmbed(1, self._PITCH_TYPE_EM_DIM)
        self.pitch_y = ContinuousEmbed(1, self._PITCH_TYPE_EM_DIM)

        # Shared layers
        self.shared = nn.Sequential(
            nn.Linear(self._PITCHER_EM_DIM*2+self._COUNT_EM_DIM*4+self._PITCH_TYPE_EM_DIM*3, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._OUTPUT_DIM)
        )
        
        self._load() 


    def forward(self, features):

        # Example: Get embeddings (2D tensors, e.g., [batch_size, embedding_dim])
        pitcher_age = self.pitcher_age(features["pitcher_age"].unsqueeze(1)) 
        batter_faces_break = self.batter_faces_break(features["batter_faces_break"]) 
       
        balls = self.balls(features["balls"])          # [batch_size, embedding_dim]
        strikes = self.strikes(features["strikes"])
        sequence = self.sequence(features["sequence"].unsqueeze(1))
        pitch_count = self.pitch_count(features["pitch_count"].unsqueeze(1))
        pitch_type = self.pitch_type(features["pitch_type_id"])
        pitch_x = self.pitch_x(features["pitch_x"].unsqueeze(1))
        pitch_y = self.pitch_x(features["pitch_y"].unsqueeze(1))


        x = torch.cat([
            pitcher_age,
            batter_faces_break,

            balls,
            strikes,
            sequence,
            pitch_count,
            pitch_type,
            pitch_x,
            pitch_y
        ], dim=1)  # [batch_size, total_features] 

        return self.shared(x)


######################################################################
######################################################################


class ContactResult(BaseModel):

    _entityType = "stadiums" 
    _leagueId = "mlb" 
    _HIT_DIM = 6
    _HIDDEN_DIM = 12
    _OUTPUT_DIM = 1

    def __init__(self, stadiumId="DEFAULT"):
        super().__init__(entityId=stadiumId, defaultId="DEFAULT")
  
        self.hitDistance = ContinuousEmbed(1, self._HIT_DIM)
        self.hitAngle = ContinuousEmbed(1, self._HIT_DIM)

        self.shared = nn.Sequential(
            nn.Linear(self._HIT_DIM*2, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._OUTPUT_DIM)
        )
        self._load()


    def forward(self, features):
        # Example: Get embeddings (2D tensors, e.g., [batch_size, embedding_dim])
        hitDistance = self.hitDistance(features["hit_distance"].unsqueeze(1))
        hitAngel = self.hitAngle(features["hit_angle"].unsqueeze(1))

        x = torch.cat([
            hitDistance, 
            hitAngel
        ], dim=1)  # [batch_size, total_features] 

        return self.shared(x)


######################################################################
######################################################################

class PitchResult(BaseModel):
    
    _entityType = "batters" 
    _leagueId = "mlb"
    _PITCHER_EM_DIM = 10
    _PITCH_TYPE_EM_DIM = 10
    _COUNT_EM_DIM = 10
    _HIDDEN_DIM = 72
    

    def __init__(self, *, entityId, defaultId=None):
        super().__init__(entityId=entityId, defaultId=defaultId)

        self.pitcher_throws_lefty = nn.Embedding(2, self._PITCHER_EM_DIM)

        self.balls =  nn.Embedding(4, self._COUNT_EM_DIM)
        self.strikes =  nn.Embedding(3, self._COUNT_EM_DIM)
        self.sequence = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_count = ContinuousEmbed(1, self._COUNT_EM_DIM)
        self.pitch_type = nn.Embedding(PITCH_TYPES, self._PITCH_TYPE_EM_DIM)
        self.pitch_x = ContinuousEmbed(1, self._PITCH_TYPE_EM_DIM)
        self.pitch_y = ContinuousEmbed(1, self._PITCH_TYPE_EM_DIM)
        self.velocity = ContinuousEmbed(1, self._PITCH_TYPE_EM_DIM)

        self.shared = nn.Sequential(
            nn.Linear(self._PITCHER_EM_DIM+self._COUNT_EM_DIM*4+self._PITCH_TYPE_EM_DIM*4, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(self._HIDDEN_DIM, self._OUTPUT_DIM)
        )
        self._load()


    def forward(self, features):

        # Example: Get embeddings (2D tensors, e.g., [batch_size, embedding_dim])
        pitcher_throws_lefty = self.pitcher_throws_lefty(features["pitcher_throws_lefty"]) 
       
        balls = self.balls(features["balls"])          # [batch_size, embedding_dim]
        strikes = self.strikes(features["strikes"])
        sequence = self.sequence(features["sequence"].unsqueeze(1))
        pitch_count = self.pitch_count(features["pitch_count"].unsqueeze(1))
        pitch_type = self.pitch_type(features["pitch_type_id"])
        pitch_x = self.pitch_x(features["pitch_x"].unsqueeze(1))
        pitch_y = self.pitch_x(features["pitch_y"].unsqueeze(1))
        velocity = self.velocity(features["velocity"].unsqueeze(1))


        x = torch.cat([
            pitcher_throws_lefty,

            balls,
            strikes,
            sequence,
            pitch_count,
            pitch_type,
            pitch_x,
            pitch_y, 
            velocity
        ], dim=1)  # [batch_size, total_features] 

        return self.shared(x)


######################################################################
######################################################################


class IsSwing(PitchResult):
    _modelName = "is_swing"
    _OUTPUT_DIM = 1


######################################################################
######################################################################


class SwingResult(PitchResult):
    _modelName = "swing_result"
    _OUTPUT_DIM = 3


######################################################################
######################################################################


class HitHardnessSelect(PitchResult):
    _modelName = "hit_hardness"
    _OUTPUT_DIM = HIT_HARDNESSES

######################################################################
######################################################################


class HitStyleSelect(PitchResult):
    _modelName = "hit_style"
    _OUTPUT_DIM = HIT_STYLES

######################################################################
######################################################################


class HitDistanceSelect(PitchResult):
    _modelName = "hit_distance"
    _OUTPUT_DIM = 1

######################################################################
######################################################################


class HitAngleSelect(PitchResult):
    _modelName = "hit_angle"
    _OUTPUT_DIM = 1


######################################################################
######################################################################


class IsHit(ContactResult):
    _modelName = "is_hit"



        

######################################################################
######################################################################


class IsHR(ContactResult):
    _modelName = "is_hr"

        



######################################################################
######################################################################


class NumBasesIfHit(ContactResult):
    _modelName = "num_bases_if_hit"
    _OUTPUT_DIM = 4






######################################################################
######################################################################

