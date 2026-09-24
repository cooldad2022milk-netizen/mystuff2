package com.csm.hybrids.client.sound;

import com.csm.hybrids.client.ClientHybridState;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;

/** Looping two-stroke idle that follows a transformed Chainsaw Hybrid and screams when the saws rev. */
public class EngineSound extends AbstractTickableSoundInstance {
    private final Player player;
    private final ClientHybridState state;

    public EngineSound(Player player, ClientHybridState state) {
        super(ModSounds.CHAINSAW_IDLE.get(), SoundSource.PLAYERS, SoundInstance.createUnseededRandom());
        this.player = player;
        this.state = state;
        this.looping = true;
        this.delay = 0;
        this.volume = 0.01f;
        this.pitch = 1f;
        this.x = player.getX();
        this.y = player.getY();
        this.z = player.getZ();
    }

    @Override
    public void tick() {
        if (player.isRemoved() || (state.type != HybridType.CHAINSAW && state.type != HybridType.CHAINSAW_DEVIL)
                || !state.transformed) {
            stop();
            return;
        }
        this.x = player.getX();
        this.y = player.getY() + 1.4;
        this.z = player.getZ();
        boolean rev = state.revving(ClientHybridState.now(0));
        float targetVol = rev ? 0.9f : 0.35f;
        float targetPitch = rev ? 1.55f : 1.0f;
        this.volume += (targetVol - volume) * 0.25f;
        this.pitch += (targetPitch - pitch) * 0.3f;
    }

    @Override
    public boolean canStartSilent() {
        return true;
    }
}
