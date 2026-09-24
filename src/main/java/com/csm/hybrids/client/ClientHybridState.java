package com.csm.hybrids.client;

import com.csm.hybrids.client.render.HybridPartsAnimatable;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.AnimSpec;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.world.entity.player.Player;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.core.animation.RawAnimation;

/**
 * Client-side animation/visibility state of one player's devil parts.
 * Time is measured in (fractional) game ticks from {@link #now(float)}.
 */
public class ClientHybridState {
    public static final RawAnimation EMERGE = RawAnimation.begin().thenPlay("emerge").thenLoop("idle");
    public static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
    public static final RawAnimation RETRACT = RawAnimation.begin().thenPlayAndHold("retract");
    public static final int RETRACT_TICKS = 8;
    /** Galgali without his mask is this much bigger. */
    public static final float VIOLENCE_SCALE = 1.3f;
    /** How deep Beam sinks into the ground while swimming through it (only the fin shows). */
    public static final double SWIM_DEPTH = 2.08;

    public final int playerId;
    public HybridType type = HybridType.NONE;
    public boolean transformed;
    public RawAnimation formAnim = IDLE;
    public double retractUntil = -1;
    public double formSince = -1;
    public String fx = "";
    public double fxUntil = -1;
    public double revUntil = -1;
    public double triggerStart = -1;
    public int triggerTicks;
    public double actionUntil = -1;
    /** Set on the frame being rendered so animation predicates can read the current time. */
    public double renderNow;
    public Object engineSound;
    private HybridPartsAnimatable animatable;
    /** Play the manifest animation on the puppet as soon as there is one (a takeover just began). */
    private boolean pendingManifest;
    /** A monster devil's form: its model, drawn in place of the player (never added to the world). */
    @Nullable
    private DevilEntity puppet;

    public ClientHybridState(int playerId) {
        this.playerId = playerId;
    }

    @Nullable
    public static ClientHybridState of(Player player) {
        HybridData data = HybridCapability.get(player);
        if (data == null) {
            return null;
        }
        if (!(data.clientState instanceof ClientHybridState)) {
            ClientHybridState st = new ClientHybridState(player.getId());
            st.type = data.type();
            st.transformed = data.isTransformed();
            data.clientState = st;
        }
        return (ClientHybridState) data.clientState;
    }

    public static double now(float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        return mc.level == null ? 0 : mc.level.getGameTime() + partialTick;
    }

    public HybridPartsAnimatable animatable() {
        if (animatable == null || animatable.type != type) {
            animatable = new HybridPartsAnimatable(type, this);
        }
        return animatable;
    }

    /** The devil model standing in for this player, or null when the type keeps a human body. */
    @Nullable
    public DevilEntity puppet(Player player) {
        if (!type.monster()) {
            return null;
        }
        if (puppet == null || puppet.devilType() != type || puppet.level() != player.level()) {
            puppet = ModEntities.devil(type).create(player.level());
            if (puppet == null) {
                return null;
            }
            puppet.owner = player;
            puppet.fxSource = group -> fxActive(group, renderNow);
        }
        if (pendingManifest) {
            pendingManifest = false;
            puppet.triggerAnim("action", "manifest");
        }
        return puppet;
    }

    /** Make the puppet stand exactly where (and how) the player does. */
    public void syncPuppet(DevilEntity p, Player player) {
        p.setPos(player.getX(), player.getY(), player.getZ());
        p.xo = player.xo;
        p.yo = player.yo;
        p.zo = player.zo;
        p.xOld = player.xOld;
        p.yOld = player.yOld;
        p.zOld = player.zOld;
        p.yBodyRot = player.yBodyRot;
        p.yBodyRotO = player.yBodyRotO;
        p.yHeadRot = player.yHeadRot;
        p.yHeadRotO = player.yHeadRotO;
        p.setYRot(player.getYRot());
        p.yRotO = player.yRotO;
        p.setXRot(player.getXRot());
        p.xRotO = player.xRotO;
        p.tickCount = player.tickCount;
        p.hurtTime = player.hurtTime;
        p.hurtDuration = player.hurtDuration;
        p.deathTime = player.deathTime;
        p.setOnGround(player.onGround());
        p.setDeltaMovement(player.getDeltaMovement());
        p.setInvisible(player.isInvisible());
    }

    public boolean formVisible(double now) {
        return transformed || now < retractUntil;
    }

    public boolean fxActive(String group, double now) {
        return group.equals(fx) && now < fxUntil;
    }

    public boolean revving(double now) {
        return now < revUntil;
    }

    /** An effect group that replaces the whole body (Beam's full shark form), or null. */
    @Nullable
    public String exclusiveFx(double now) {
        return fxActive("sharkform", now) ? "sharkform" : null;
    }

    /** Whole-body render scale (Galgali grows when the mask comes off). */
    public float renderScale(double now) {
        if (type != HybridType.VIOLENCE) {
            return 1f;
        }
        double f;
        if (transformed) {
            f = formSince < 0 ? 1 : Math.min(1, Math.max(0, (now - formSince) / 10.0));
        } else if (now < retractUntil) {
            f = Math.max(0, (retractUntil - now) / RETRACT_TICKS);
        } else {
            return 1f;
        }
        f = f * f * (3 - 2 * f);
        return (float) (1 + (VIOLENCE_SCALE - 1) * f);
    }

    /** How far the body is sunk into the ground (Beam swimming through it). */
    public double sink(double now) {
        return fxActive("swim", now) ? SWIM_DEPTH : 0;
    }

    /** Seconds into the transformation trigger animation, or -1 when none is playing. */
    public double triggerSeconds(double now) {
        if (triggerStart < 0) {
            return -1;
        }
        double t = (now - triggerStart) / 20.0;
        return t >= 0 && t <= triggerTicks / 20.0 + 0.5 ? t : -1;
    }

    // ------------------------------------------------------------------ network
    public void onSync(HybridType oldType, boolean wasTransformed, HybridData data) {
        double now = now(0);
        this.type = data.type();
        if (oldType != data.type()) {
            animatable = null;
            formAnim = IDLE;
            retractUntil = -1;
            if (data.isTransformed() && type.monster()) {
                // a hybrid taken over by its devil: the devil's body stands up out of it
                formSince = now;
                pendingManifest = true;
            }
        } else if (!wasTransformed && data.isTransformed()) {
            formAnim = EMERGE;
            retractUntil = -1;
            formSince = now;
            if (puppet != null && type.monster()) {
                puppet.triggerAnim("action", "manifest");
            }
        } else if (wasTransformed && !data.isTransformed()) {
            formAnim = RETRACT;
            retractUntil = now + RETRACT_TICKS;
            if (puppet != null && type.monster()) {
                puppet.triggerAnim("action", "retract");
            }
        }
        this.transformed = data.isTransformed();
    }

    public void onAnim(AnimSpec spec, AbstractClientPlayer player) {
        double now = now(0);
        if (spec.kind() == AnimSpec.STOP) {
            PlayerAnims.stop(player);
            fx = "";
            revUntil = -1;
            triggerStart = -1;
            actionUntil = -1;
            return;
        }
        if (!spec.playerAnim().isEmpty()) {
            PlayerAnims.play(player, spec.playerAnim());
        }
        if (spec.kind() == AnimSpec.TRANSFORM) {
            triggerStart = now;
            triggerTicks = spec.duration();
        }
        actionUntil = now + spec.duration();
        if (!spec.fx().isEmpty()) {
            fx = spec.fx();
            fxUntil = now + spec.duration();
        }
        if (spec.revs()) {
            revUntil = now + spec.duration();
        }
        if (!spec.geoAnim().isEmpty() && type != HybridType.NONE) {
            if (type.monster()) {
                DevilEntity p = puppet(player);
                if (p != null && spec.kind() == AnimSpec.ABILITY) {
                    p.triggerAnim("action", spec.geoAnim());
                }
            } else {
                animatable().trigger(spec.controller(), spec.geoAnim());
            }
        }
    }
}
