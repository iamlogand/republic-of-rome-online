import random
from typing import List
from django.test import TestCase
from rest_framework.test import APIClient
from rorapp.functions import delete_all_games, generate_game, start_game
from rorapp.functions.faction_leader_helper import select_faction_leader
from rorapp.functions.forum_phase_starter import start_forum_phase
from rorapp.functions.progress_helper import get_step
from rorapp.functions.war_helper import create_new_war
from rorapp.functions.enemy_leader_helper import create_new_enemy_leader
from rorapp.models import (
    Action,
    ActionLog,
    EnemyLeader,
    Faction,
    Game,
    Player,
    Secret,
    Senator,
    Situation,
    Title,
    War,
)
from rorapp.tests.test_helper import (
    check_latest_phase,
    check_old_actions_deleted,
    get_and_check_actions,
    submit_actions,
)


class ForumPhaseTests(TestCase):
    """
    Ensure that players can select their faction leader during the forum phase.
    """

    def test_forum_phase(self) -> None:
        """
        Ensure the forum phase generally works.
        """

        delete_all_games()
        for player_count in range(3, 7):
            self.do_forum_phase_test(player_count)

    def test_new_family(self) -> None:
        """
        Ensure that a new senator is created when the new family situation is initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)

        # Delete all non-senator situations to ensure that the next situation is a senator situation
        non_senator_situations = Situation.objects.filter(game=game_id).exclude(
            type="senator"
        )
        non_senator_situations.delete()

        # Ensure that there are only senator situations and the correct number of situations remain
        remaining_situations = Situation.objects.filter(game=game_id)
        # There should be 11 senator situations at the start of a 3-player game
        STARTING_SENATOR_SITUATION_COUNT = 11
        self.assertEqual(remaining_situations.count(), 11)
        for situation in remaining_situations:
            self.assertEqual(situation.type, "senator")

        original_senator_count = Senator.objects.filter(game=game_id).count()

        # Initiate senator situation
        self.initiate_situation(game_id)
        new_family_action_log = self.get_and_check_latest_action_log(
            game_id, "new_family"
        )
        self.assertEqual(new_family_action_log.data["initiating_faction"], faction.id)
        new_senator_id = new_family_action_log.data["senator"]
        new_senator = Senator.objects.get(id=new_senator_id)

        remaining_situations = Situation.objects.filter(game=game_id)
        self.assertEqual(
            remaining_situations.count(), STARTING_SENATOR_SITUATION_COUNT - 1
        )
        remaining_situation_senator_names = [
            situation.name for situation in remaining_situations
        ]
        self.assertNotIn(new_senator.name, remaining_situation_senator_names)

        new_senator_count = Senator.objects.filter(game=game_id).count()
        self.assertEqual(new_senator_count, original_senator_count + 1)

    def test_new_war(self) -> None:
        """
        Ensure that a new war is created when the new war situation is initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)

        # Delete all non-war situations to ensure that the next situation is a senator situation
        Situation.objects.filter(game=game_id).exclude(type="war").delete()

        # Ensure that there are only war situations and the correct number of situations remain
        remaining_situations = Situation.objects.filter(game=game_id)
        # There should be 7 war situations at the start of the game
        # There are 8 wars in the Early Republic, but one is already out: the 1st Punic War
        STARTING_WAR_SITUATION_COUNT = 7
        STARTING_WAR_COUNT = 1
        self.assertEqual(remaining_situations.count(), STARTING_WAR_SITUATION_COUNT)
        for situation in remaining_situations:
            self.assertEqual(situation.type, "war")

        war_count = War.objects.filter(game=game_id).count()
        self.assertEqual(war_count, STARTING_WAR_COUNT)

        # Initiate new war situation
        self.initiate_situation(game_id)
        new_war_action_log = self.get_and_check_latest_action_log(game_id, "new_war")
        self.assertEqual(new_war_action_log.data["initiating_faction"], faction.id)
        new_war_id = new_war_action_log.data["war"]
        new_war = War.objects.get(id=new_war_id)

        remaining_situations = Situation.objects.filter(game=game_id)
        self.assertEqual(remaining_situations.count(), STARTING_WAR_SITUATION_COUNT - 1)
        remaining_situation_war_names = [
            situation.name for situation in remaining_situations
        ]
        new_war_full_name = f"{new_war.name} {new_war.index}"
        self.assertNotIn(new_war_full_name, remaining_situation_war_names)

        war_count = War.objects.filter(game=game_id).count()
        self.assertEqual(war_count, STARTING_WAR_COUNT + 1)

    def test_matching_war(self) -> None:
        """
        Ensure that the 1st Punic War is activated when the 2nd Punic War is initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)

        # Ensure that the next situation is the 2nd Punic War
        situation = Situation.objects.get(game=game_id, type="war", name="Punic 2")
        situation.index = 100
        situation.save()

        self.initiate_situation(game_id)

        new_war_action_log = self.get_and_check_latest_action_log(game_id, "new_war", 1)
        self.assertEqual(new_war_action_log.data["initiating_faction"], faction.id)
        matched_war_action_log = self.get_and_check_latest_action_log(
            game_id, "matched_war"
        )
        war = War.objects.get(id=matched_war_action_log.data["war"])
        self.assertEqual(war.name, "Punic")
        self.assertEqual(war.index, 1)
        self.assertEqual(war.status, "active")
        new_war = War.objects.get(id=matched_war_action_log.data["new_war"])
        self.assertEqual(new_war.name, "Punic")
        self.assertEqual(new_war.index, 2)
        self.assertEqual(new_war.status, "imminent")
        self.assertEqual(matched_war_action_log.data["new_status"], "active")

    def test_matching_war_reverse_order(self) -> None:
        """
        Ensure that the 2nd Macedonian war is activated when the 1st Macedonian War is initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)
        create_new_war(faction.id, "Macedonian 2")
        self.get_and_check_latest_action_log(game_id, "new_war")

        # Ensure that the next situation is the 1st Macedonian War
        situation = Situation.objects.get(game=game_id, type="war", name="Macedonian 1")
        situation.index = 100
        situation.save()

        self.initiate_situation(game_id)
        new_war_action_log = self.get_and_check_latest_action_log(game_id, "new_war", 1)
        self.assertEqual(new_war_action_log.data["initiating_faction"], faction.id)
        matched_war_action_log = self.get_and_check_latest_action_log(
            game_id, "matched_war"
        )
        war = War.objects.get(id=matched_war_action_log.data["war"])
        self.assertEqual(war.name, "Macedonian")
        self.assertEqual(war.index, 2)
        self.assertEqual(war.status, "active")
        new_war = War.objects.get(id=matched_war_action_log.data["new_war"])
        self.assertEqual(new_war.name, "Macedonian")
        self.assertEqual(new_war.index, 1)
        self.assertEqual(new_war.status, "imminent")
        self.assertEqual(matched_war_action_log.data["new_status"], "active")

    def test_create_leader_then_new_war(self) -> None:
        """
        Ensure that Philip V joins and activates the matching 2nd Macedonian War when it's initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)
        create_new_enemy_leader(faction.id, "Philip V")

        # Ensure that the next situation is the 2nd Macedonian War
        situation = Situation.objects.get(game=game_id, type="war", name="Macedonian 2")
        situation.index = 100
        situation.save()

        self.initiate_situation(game_id)
        new_war_action_log = self.get_and_check_latest_action_log(game_id, "new_war", 1)
        self.assertEqual(new_war_action_log.data["initiating_faction"], faction.id)
        matched_enemy_leader_action_log = self.get_and_check_latest_action_log(
            game_id, "matched_enemy_leader"
        )
        enemy_leader = EnemyLeader.objects.get(
            id=matched_enemy_leader_action_log.data["enemy_leader"]
        )
        self.assertEqual(
            new_war_action_log.data["activating_enemy_leaders"][0], enemy_leader.id
        )
        self.assertEqual(enemy_leader.name, "Philip V")
        new_war = War.objects.get(id=matched_enemy_leader_action_log.data["new_war"])
        assert isinstance(enemy_leader.current_war, War)
        self.assertEqual(enemy_leader.current_war.id, new_war.id)
        self.assertEqual(new_war.name, "Macedonian")
        self.assertEqual(new_war.index, 2)
        self.assertEqual(new_war.status, "active")

    def test_create_leader_then_new_inherently_active_war(self) -> None:
        """
        Ensure that Philip V joins the matching and inherently active 1st Macedonian War when it's initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)
        create_new_enemy_leader(faction.id, "Philip V")

        # Ensure that the next situation is the 1st Macedonian War
        situation = Situation.objects.get(game=game_id, type="war", name="Macedonian 1")
        situation.index = 100
        situation.save()

        self.initiate_situation(game_id)
        new_war_action_log = self.get_and_check_latest_action_log(game_id, "new_war", 1)
        self.assertEqual(new_war_action_log.data["initiating_faction"], faction.id)
        matched_enemy_leader_action_log = self.get_and_check_latest_action_log(
            game_id, "matched_enemy_leader"
        )
        enemy_leader = EnemyLeader.objects.get(
            id=matched_enemy_leader_action_log.data["enemy_leader"]
        )
        self.assertFalse("activating_enemy_leaders" in new_war_action_log.data)
        self.assertEqual(enemy_leader.name, "Philip V")
        new_war = War.objects.get(id=matched_enemy_leader_action_log.data["new_war"])
        assert isinstance(enemy_leader.current_war, War)
        self.assertEqual(enemy_leader.current_war.id, new_war.id)
        self.assertEqual(new_war.name, "Macedonian")
        self.assertEqual(new_war.index, 1)
        self.assertEqual(new_war.status, "active")

    def test_create_enemy_leaders_then_new_war(self) -> None:
        """
        Ensure that Hamilcar and Hannibal join the matching and inherently active 2nd Punic War when it's initiated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)

        # Mark the 1st Punic War as defeated to ensure that Hamilcar and Hannibal join the 2nd Punic War when it comes up
        first_punic_war = War.objects.get(game=game_id, name="Punic", index=1)
        first_punic_war.status = "defeated"
        first_punic_war.save()

        create_new_enemy_leader(faction.id, "Hamilcar")
        create_new_enemy_leader(faction.id, "Hannibal")

        # Ensure that the next situation is the 2nd Punic War
        situation = Situation.objects.get(game=game_id, type="war", name="Punic 2")
        situation.index = 100
        situation.save()

        self.initiate_situation(game_id)
        new_war_action_log = self.get_and_check_latest_action_log(game_id, "new_war", 2)
        self.assertEqual(new_war_action_log.data["initiating_faction"], faction.id)
        matched_enemy_leader_action_logs = [
            self.get_and_check_latest_action_log(game_id, "matched_enemy_leader"),
            self.get_and_check_latest_action_log(game_id, "matched_enemy_leader", 1),
        ]
        enemy_leader_ids = []
        for action_log in matched_enemy_leader_action_logs:
            enemy_leader_ids.append(action_log.data["enemy_leader"])
            self.assertFalse("activating_enemy_leaders" in new_war_action_log.data)

        enemy_leaders = EnemyLeader.objects.filter(id__in=enemy_leader_ids)
        self.assertEqual(enemy_leaders.count(), 2)
        sorted_enemy_leader_list = sorted(
            list(enemy_leaders), key=lambda leader: leader.name
        )
        self.assertEqual(sorted_enemy_leader_list[0].name, "Hamilcar")
        self.assertEqual(sorted_enemy_leader_list[1].name, "Hannibal")

    def test_existing_war_then_new_enemy_leader(self) -> None:
        """
        Ensure that when Hannibal is initiated, he joins and activates the matching 1st Punic War.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)

        # Ensure that the next situation is Hannibal
        situation = Situation.objects.get(game=game_id, type="leader", name="Hannibal")
        situation.index = 100
        situation.save()

        self.initiate_situation(game_id)
        new_enemy_leader_action_log = self.get_and_check_latest_action_log(
            game_id, "new_enemy_leader", 1
        )
        self.assertEqual(
            new_enemy_leader_action_log.data["initiating_faction"], faction.id
        )
        enemy_leader_id = new_enemy_leader_action_log.data["enemy_leader"]
        matched_war_action_log = self.get_and_check_latest_action_log(
            game_id, "matched_war"
        )
        self.assertEqual(
            matched_war_action_log.data["new_enemy_leader"], enemy_leader_id
        )
        enemy_leader = EnemyLeader.objects.get(id=enemy_leader_id)
        self.assertEqual(enemy_leader.name, "Hannibal")

    def test_new_secret(self) -> None:
        """
        Ensure that a secret and an action log are issued when a faction initiates the related situation.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        faction = Faction.objects.get(game=game_id, position=1)

        # Delete all non-secret situations to ensure that the next situation is a secret
        Situation.objects.filter(game=game_id).filter(secret=False).delete()
        next_secret_situation = (
            Situation.objects.filter(game=game_id).order_by("-index").first()
        )
        assert isinstance(next_secret_situation, Situation)
        initial_secret_count = Secret.objects.filter(faction__game=game_id).count()

        self.initiate_situation(game_id)
        new_secret_action_log = self.get_and_check_latest_action_log(
            game_id, "new_secret"
        )
        assert isinstance(new_secret_action_log.faction, Faction)
        self.assertEqual(new_secret_action_log.faction.id, faction.id)
        secrets = Secret.objects.filter(faction__game=game_id)
        self.assertEqual(secrets.count(), initial_secret_count + 1)
        self.assertTrue(
            next_secret_situation.name in [secret.name for secret in secrets]
        )

    def test_new_concession_secret(self) -> None:
        """
        Ensure that a concession secret and an action log are issued when a faction initiates the related situation.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, position=1)

        # Delete all situations and create a concession situation
        Situation.objects.filter(game=game_id).filter(secret=False).delete()
        armaments_situation = Situation(
            name="Armaments", type="concession", secret=True, game=game, index=0
        )
        armaments_situation.save()
        secrets = Secret.objects.filter(faction__game=game_id)
        initial_secret_count = secrets.count()

        self.initiate_situation(game_id)
        new_secret_action_log = self.get_and_check_latest_action_log(
            game_id, "new_secret"
        )
        assert isinstance(new_secret_action_log.faction, Faction)
        self.assertEqual(new_secret_action_log.faction.id, faction.id)
        self.assertEqual(secrets.count(), initial_secret_count + 1)
        armaments_secret_count = 0
        for secret in secrets:
            if secret.name == "Armaments":
                self.assertEqual(secret.type, "concession")
                armaments_secret_count += 1
        self.assertEqual(armaments_secret_count, 1)

    def test_new_statesman_secret(self) -> None:
        """
        Ensure that a statesman secret and an action log are issued when a faction initiates the related situation.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)
        game = Game.objects.get(id=game_id)
        faction = Faction.objects.get(game=game_id, position=1)

        # Delete all situations and create a statesman situation
        Situation.objects.filter(game=game_id).filter(secret=False).delete()
        armaments_situation = Situation(
            name="P. Cornelius Scipio Africanus",
            type="statesman",
            secret=True,
            game=game,
            index=0,
        )
        armaments_situation.save()
        secrets = Secret.objects.filter(faction__game=game_id)
        initial_secret_count = secrets.count()

        self.initiate_situation(game_id)
        new_secret_action_log = self.get_and_check_latest_action_log(
            game_id, "new_secret"
        )
        assert isinstance(new_secret_action_log.faction, Faction)
        self.assertEqual(new_secret_action_log.faction.id, faction.id)
        self.assertEqual(secrets.count(), initial_secret_count + 1)
        armaments_secret_count = 0
        for secret in secrets:
            if secret.name == "P. Cornelius Scipio Africanus":
                self.assertEqual(secret.type, "statesman")
                armaments_secret_count += 1
        self.assertEqual(armaments_secret_count, 1)

    def test_era_ends(self) -> None:
        """
        Ensure that once all situations have been initiated, the "era_ends" action log is generated and the phase becomes the Final Forum Phase.
        Check that the game ends (no potential actions) once the Final Forum Phase is over, and that the "faction_wins" action log is generated.
        """

        game_id, _ = self.setup_game_in_forum_phase(3)

        # Delete all situations except for one to ensure that the next situation is the last one
        Situation.objects.filter(game=game_id).exclude(index=0).delete()

        self.initiate_situation(game_id)
        self.get_and_check_latest_action_log(game_id, "era_ends")

        check_latest_phase(self, game_id, "Final Forum")
        self.submit_select_faction_leader_actions(game_id)
        self.check_potential_action_count(game_id, 1)
        self.submit_select_faction_leader_actions(game_id)
        self.check_potential_action_count(game_id, 1)
        self.submit_select_faction_leader_actions(game_id)
        self.check_potential_action_count(game_id, 0)

        faction_wins_action_log = self.get_and_check_latest_action_log(
            game_id, "faction_wins"
        )
        self.assertIsNotNone(faction_wins_action_log.faction)
        self.assertEqual(faction_wins_action_log.data["type"], "influence")

    def submit_select_faction_leader_actions(self, game_id: int) -> None:
        potential_actions = get_and_check_actions(
            self, game_id, False, "select_faction_leader", 1
        )
        submit_actions(
            self, game_id, potential_actions, self.faction_leader_action_processor
        )

    def check_potential_action_count(self, game_id: int, expected_count: int) -> None:
        step = get_step(game_id)
        completed_actions = Action.objects.filter(step=step, completed=False)
        self.assertEqual(completed_actions.count(), expected_count)

    def initiate_situation(self, game_id: int) -> None:
        check_latest_phase(self, game_id, "Forum")
        situation_potential_actions = get_and_check_actions(
            self, game_id, False, "initiate_situation", 1
        )
        submit_actions(
            self,
            game_id,
            situation_potential_actions,
        )

    def get_and_check_latest_action_log(
        self, game_id: int, expected_type: str, reverse_index: int = 0
    ) -> ActionLog:
        latest_action_log = ActionLog.objects.filter(
            step__phase__turn__game=game_id
        ).order_by("-index")[reverse_index]
        self.assertEqual(latest_action_log.type, expected_type)
        return latest_action_log

    def faction_leader_action_processor(self, action: Action) -> dict:
        assert isinstance(action.faction.player, Player)
        faction = Faction.objects.filter(player=action.faction.player.id).get(
            game=action.faction.game.id
        )
        senators = Senator.objects.filter(faction=faction).order_by("name")
        first_senator = senators[0]
        return {"leader_id": first_senator.id}

    def do_forum_phase_test(self, player_count: int) -> None:
        game_id, faction_ids_with_leadership = self.setup_game_in_forum_phase(
            player_count
        )

        # Ensure that the game starts with correct number of situations
        situations = Situation.objects.filter(game=game_id)
        self.assertEqual(situations.count(), 63 - player_count * 6)

        for _ in range(0, player_count):
            check_latest_phase(self, game_id, "Forum")
            situation_potential_actions = get_and_check_actions(
                self, game_id, False, "initiate_situation", 1
            )
            submit_actions(
                self,
                game_id,
                situation_potential_actions,
            )
            check_latest_phase(self, game_id, "Forum")
            faction_leader_potential_actions = get_and_check_actions(
                self, game_id, False, "select_faction_leader", 1
            )
            faction_leader_titles = Title.objects.filter(
                name="Faction Leader",
                senator__faction=faction_leader_potential_actions[0].faction,
                end_step=None,
            )

            # If the faction already has a leader, then there should be no existing faction leader title.
            self.assertEqual(
                len(faction_leader_titles),
                1
                if faction_leader_potential_actions[0].faction.id
                in faction_ids_with_leadership
                else 0,
            )
            submit_actions(
                self,
                game_id,
                faction_leader_potential_actions,
                self.faction_leader_action_processor,
            )
            faction_leader_titles = Title.objects.filter(
                name="Faction Leader",
                senator__faction=faction_leader_potential_actions[0].faction,
                end_step=None,
            )
            self.assertEqual(len(faction_leader_titles), 1)
        check_latest_phase(self, game_id, "Revolution")
        check_old_actions_deleted(self, game_id)

    def setup_game_in_forum_phase(self, player_count: int) -> tuple[int, List[int]]:
        self.client = APIClient()
        random.seed(1)
        game_id = generate_game(player_count)
        start_game(game_id)
        faction_ids_with_leadership = set_some_faction_leaders(game_id)
        start_forum_phase(game_id)
        return (game_id, faction_ids_with_leadership)


def set_some_faction_leaders(game_id: int) -> List[int]:
    """
    Assigns faction leader titles to 2 senators then returns their faction IDs.
    """
    factions = Faction.objects.filter(game=game_id)
    first_faction = factions.first()
    second_faction = factions.last()

    assert isinstance(first_faction, Faction)
    assert isinstance(second_faction, Faction)

    senator_in_faction_1 = Senator.objects.filter(
        game=game_id, faction=first_faction
    ).first()
    senator_in_faction_2 = Senator.objects.filter(
        game=game_id, faction=second_faction
    ).first()

    assert isinstance(senator_in_faction_1, Senator)
    assert isinstance(senator_in_faction_2, Senator)

    select_faction_leader(senator_in_faction_1.id)
    select_faction_leader(senator_in_faction_2.id)
    return [
        first_faction.id,
        second_faction.id,
    ]
