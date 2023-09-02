# Package used to group the view scripts
from .faction import FactionViewSet
from .game import GameViewSet
from .index import index
from .notification import NotificationViewSet
from .player import PlayerViewSet
from .phase import PhaseViewSet
from .potential_action import PotentialActionViewSet
from .senator import SenatorViewSet
from .start_game import StartGameViewSet
from .step import StepViewSet
from .submit_action import SubmitActionViewSet
from .title import TitleViewSet
from .token import MyTokenObtainPairView, TokenObtainPairByEmailView
from .turn import TurnViewSet
from .user import UserViewSet
from .waitlist_entry import WaitlistEntryViewSet
