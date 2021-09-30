from events.MoonriseArtifacts.Artifact import Artifact


class Diamond(Artifact):
    def __init__(self,
                 name="A shining diamond",
                 description="This gem shines with an internal light. Cicero looks at it oddly. \"It would make a "
                             "fantastic flashlight. It's definitely from a god, but I have no idea which one.\"",
                 uses=1,
                 cost="10l"):
        Artifact.__init__(self, name, description, uses, cost)
