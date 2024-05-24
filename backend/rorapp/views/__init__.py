# Package used to group the view scripts
from .action import ActionViewSet  # noqa: F401
from .action_log import ActionLogViewSet  # noqa: F401
from .concession import ConcessionViewSet  # noqa: F401
from .enemy_leader import EnemyLeaderViewSet  # noqa: F401
from .faction import FactionViewSet  # noqa: F401
from .game import GameViewSet  # noqa: F401
from .index import index  # noqa: F401
from .phase import PhaseViewSet  # noqa: F401
from .player import PlayerViewSet  # noqa: F401
from .secret import SecretPrivateViewSet, SecretPublicViewSet  # noqa: F401
from .senator import SenatorViewSet  # noqa: F401
from .senator_action_log import SenatorActionLogViewSet  # noqa: F401
from .start_game import StartGameViewSet  # noqa: F401
from .step import StepViewSet  # noqa: F401
from .submit_action import SubmitActionViewSet  # noqa: F401
from .title import TitleViewSet  # noqa: F401
from .token import MyTokenObtainPairView, TokenObtainPairByEmailView  # noqa: F401
from .turn import TurnViewSet  # noqa: F401
from .user import UserViewSet  # noqa: F401
from .waitlist_entry import WaitlistEntryViewSet  # noqa: F401
from .war import WarViewSet  # noqa: F401
