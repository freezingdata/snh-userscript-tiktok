from tiktok.tiktok_debug import *
from tiktok.tiktok_profile_collector import TiktokProfileCollector
from snhwalker_utils.utils import print_start_and_end


@print_start_and_end
def upgrade_task_item(task_item):
    """
    Takes task_item dict without a "TargetProfile" entry and updates it with necessary data
    from 'DictSNUserData' type by saving the profile provided in the given URL to update the "TargetProfile".
    """
    target_url = task_item.get("TargetURL", "")
    # TODO: Most likely need to create url_checker. Link validation, availability.
    if not target_url:
        debugPrint("Incorrectly data in task_item")
        raise Exception("funk: upgrade_task_item, task_item have not necessary key")
        # TODO: Most likely need to create our own snh_error_messages and our own snh_exceptions.
    debugPrint(target_url)
    current_profile_snh = TiktokProfileCollector().save_profile(target_url)
    task_item["Targetprofile"] = current_profile_snh
