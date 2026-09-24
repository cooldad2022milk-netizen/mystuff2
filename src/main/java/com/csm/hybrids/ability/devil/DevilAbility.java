package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * A full devil's move. The same code runs for a player who has become the devil (from the ability wheel) and for the
 * devil fighting as a mob ({@link com.csm.hybrids.entity.devil.DevilMoveGoal}): {@link #begin}, then {@link #perform}
 * every tick with {@code run.tick} counting up, then {@link #finish}.
 * <p>
 * The AI hints ({@link #ai}) tell the mob when the move makes sense: distance to the target (edge to edge) and how
 * often to pick it.
 */
public abstract class DevilAbility extends Ability {
    public double aiMin = 0;
    public double aiMax = 4;
    public int aiWeight = 10;
    /** The mob stands still and faces its target while performing it. */
    public boolean rooted = true;
    public boolean needsSight = true;
    /** Whether the mob version uses this move at all (some moves only make sense for a player). */
    public boolean mobUse = true;
    /** How far a player's crosshair picks a target when the move starts. */
    protected double reach = 32;

    protected DevilAbility(HybridType type, String id) {
        super(type, id);
    }

    protected DevilAbility ai(double min, double max, int weight) {
        this.aiMin = min;
        this.aiMax = max;
        this.aiWeight = weight;
        return this;
    }

    protected DevilAbility mobile() {
        this.rooted = false;
        return this;
    }

    protected DevilAbility blind() {
        this.needsSight = false;
        return this;
    }

    protected DevilAbility playerOnly() {
        this.mobUse = false;
        return this;
    }

    protected DevilAbility reach(double reach) {
        this.reach = reach;
        return this;
    }

    // ---------------------------------------------------------------- player entry points
    @Override
    public void start(ServerPlayer player, HybridData data, AbilityRun run) {
        begin(player, run);
    }

    @Override
    public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
        perform(player, run);
    }

    @Override
    public void end(ServerPlayer player, HybridData data, AbilityRun run) {
        finish(player, run);
    }

    // ---------------------------------------------------------------- shared
    /** Called once when the move starts; picks the target under the crosshair (the mob sets its own target first). */
    public void begin(LivingEntity user, AbilityRun run) {
        if (run.target == null) {
            EntityHitResult hit = AbilityUtil.raycastEntity(user, reach);
            if (hit != null) {
                run.target = hit.getEntity();
            }
        }
    }

    public abstract void perform(LivingEntity user, AbilityRun run);

    /** Extra conditions for the mob to pick this move (e.g. only when it is badly hurt). */
    public boolean aiReady(com.csm.hybrids.entity.devil.DevilEntity mob, LivingEntity target) {
        return true;
    }

    public void finish(LivingEntity user, AbilityRun run) {
    }

    /**
     * Everything in a cone in front of the user, plus the move's own target (the one under the crosshair when it
     * started, or the mob's quarry) as long as it is within range and in sight: aiming at something means hitting it.
     */
    protected static java.util.List<LivingEntity> coneTargets(LivingEntity user, AbilityRun run,
                                                                net.minecraft.world.phys.Vec3 from,
                                                                net.minecraft.world.phys.Vec3 dir, double range,
                                                                double halfAngle) {
        java.util.List<LivingEntity> out = new java.util.ArrayList<>(AbilityUtil.inCone(user, from, dir, range, halfAngle));
        LivingEntity t = target(run);
        if (t != null && !out.contains(t) && AbilityUtil.canHit(user, t)
                && t.getBoundingBox().getCenter().distanceTo(from) <= range + t.getBbWidth() && user.hasLineOfSight(t)) {
            out.add(0, t);
        }
        return out;
    }

    /** The move's target if it is still alive. */
    @Nullable
    protected static LivingEntity target(AbilityRun run) {
        return run.target instanceof LivingEntity l && l.isAlive() ? l : null;
    }

    protected static ServerLevel level(LivingEntity user) {
        return (ServerLevel) user.level();
    }
}
