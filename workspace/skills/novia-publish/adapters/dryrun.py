"""Adaptateur de simulation : n'envoie rien, décrit ce qui serait publié. Jamais compté comme publication."""


def publish(channel, settings, caption, assets, manifest):
    return {
        "state": "simulated",
        "id": "dryrun-%s" % manifest["id"],
        "url": None,
        "message": "simulation %s : %d fichier(s), légende %d caractères" % (channel, len(assets), len(caption)),
        "would_send": {"channel": channel, "assets": assets, "caption": caption[:200]},
    }
