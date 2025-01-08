from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import (
    PermissionDenied,
    MethodNotAllowed,
    ValidationError,
)
from rorapp.functions import (
    send_websocket_messages,
    create_websocket_message,
)
from rorapp.models import Faction
from rorapp.serializers import FactionSerializer, FactionUpdateSerializer


FACTION_COLORS = {1: "red", 2: "yellow", 3: "green", 4: "cyan", 5: "blue", 6: "purple"}


class FactionViewSet(viewsets.ModelViewSet):
    """
    Read and partial update factions. Partial updates only affect the `custom_name` field.
    """

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Allow only GET and PATCH methods
        if self.action in ["list", "retrieve", "partial_update"]:
            return [permission() for permission in self.permission_classes]
        else:
            raise MethodNotAllowed(self.request.method)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return FactionUpdateSerializer
        else:
            return FactionSerializer

    def get_queryset(self):
        queryset = Faction.objects.all()

        # Filter against a `game` query parameter in the URL
        game_id = self.request.query_params.get("game", None)
        if game_id is not None:
            queryset = queryset.filter(game__id=game_id)

        return queryset

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            # Update (PUT) is not allowed, but partial update (PATCH) is allowed
            raise MethodNotAllowed("PUT")
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def perform_update(self, serializer):
        # Get this game instance
        faction = serializer.instance

        # Only allow if sender controls this faction
        if faction.player.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this faction.")

        # Only allow if faction doesn't already have a custom name
        if faction.custom_name is not None:
            raise PermissionDenied(
                "You can't change a faction's name once it's already been set."
            )

        # Format the custom name (strip whitespace)
        unformatted_name = serializer.validated_data["custom_name"]
        serializer.validated_data["custom_name"] = unformatted_name.strip()

        # Only allow if the custom name is not blank
        if len(serializer.validated_data["custom_name"]) == 0:
            raise ValidationError(
                {"custom_name": ["Your faction's name can't be blank."]}
            )

        # Only allow if the custom name doesn't reference another faction's color
        other_factions = Faction.objects.filter(game=faction.game).exclude(
            position=faction.position
        )
        other_faction_positions = [faction.position for faction in other_factions]
        blacklisted_colors = [
            FACTION_COLORS[position] for position in other_faction_positions
        ]
        for color in blacklisted_colors:
            if color in serializer.validated_data["custom_name"].lower():
                raise ValidationError(
                    {
                        "custom_name": [
                            f"Your faction's name can't reference another faction's color: {color.capitalize()}."
                        ]
                    }
                )

        # Only allow if the custom name is somewhat distinct from the default name
        custom_name = serializer.validated_data["custom_name"].lower()
        if (
            custom_name == FACTION_COLORS[faction.position]
            or custom_name == FACTION_COLORS[faction.position] + " faction"
            or custom_name == "faction"
        ):
            raise ValidationError({"custom_name": ["That's not a very creative name."]})

        # Only allow if no other factions in this game have the same custom name
        if Faction.objects.filter(
            game=faction.game,
            custom_name__iexact=serializer.validated_data["custom_name"],
        ).exists():
            raise ValidationError(
                {"custom_name": ["Another faction in this game already has this name."]}
            )

        # Update the game
        super().perform_update(serializer)

        # Send a WebSocket message
        messages_to_send = [
            create_websocket_message("faction", FactionSerializer(faction).data)
        ]
        send_websocket_messages(faction.game.id, messages_to_send)
