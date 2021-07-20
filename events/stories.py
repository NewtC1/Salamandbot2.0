import asyncio
import time
import utils.helper_functions as hf


class StoryManager:

    def __init__(self, tick_rate=3600, removal_cache=1):
        self.tick_rate = tick_rate
        self.removal_cache = removal_cache
        self.story_timer = time.time()

    async def tick(self):
        """Required tick function"""
        # roll a new story every 3 hours
        if time.time() > self.story_timer + self.tick_rate:
            if hf.get_selected_stories_list() > 0:
                hf.roll_story()

            self.story_timer = time.time() + 3600

        return
