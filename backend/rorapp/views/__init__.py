# Package used to group the view scripts
from .index import index
from .game import GameViewSet
from .token import MyTokenObtainPairView, TokenObtainPairByEmailView
from .user import UserViewSet
from .game_participant import GameParticipantViewSet
from .waitlist_entry import WaitlistEntryViewSet
from .start_game import StartGameViewset
from .family_senator import FamilySenatorViewSet
from .faction import FactionViewSet
from .office import OfficeViewSet
