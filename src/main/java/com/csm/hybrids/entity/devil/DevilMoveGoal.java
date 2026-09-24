package com.csm.hybrids.entity.devil;

import com.csm.hybrids.ability.devil.DevilAbility;
import com.csm.hybrids.devil.DevilSpec;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;
import java.util.List;

/**
 * How a devil fights: close to its preferred distance, then pick one of its moves that fits the range (weighted,
 * each on its own cooldown). While a move runs {@link DevilEntity} ticks it; this goal just waits.
 */
public class DevilMoveGoal extends Goal {
    private final DevilEntity mob;
    private final List<DevilAbility> moves;
    private final int[] cooldowns;
    private int pause = 20;
    private int repath;

    public DevilMoveGoal(DevilEntity mob) {
        this.mob = mob;
        this.moves = mob.moves();
        this.cooldowns = new int[moves.size()];
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity t = mob.getTarget();
        return t != null && t.isAlive();
    }

    @Override
    public boolean canContinueToUse() {
        return mob.activeRun != null || canUse();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void start() {
        pause = 10 + mob.getRandom().nextInt(15);
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
    }

    @Override
    public void tick() {
        for (int i = 0; i < cooldowns.length; i++) {
            if (cooldowns[i] > 0) {
                cooldowns[i]--;
            }
        }
        if (mob.activeRun != null) {
            return;
        }
        LivingEntity target = mob.getTarget();
        if (target == null || !target.isAlive()) {
            return;
        }
        DevilSpec spec = mob.spec();
        double dist = Math.max(0, mob.distanceTo(target) - (target.getBbWidth() + mob.getBbWidth()) * 0.5);
        boolean sight = mob.getSensing().hasLineOfSight(target);
        mob.getLookControl().setLookAt(target, 30f, 30f);
        if (!spec.stationary) {
            if (dist > spec.preferredRange || !sight) {
                if (--repath <= 0) {
                    repath = 8 + mob.getRandom().nextInt(6);
                    if (spec.flying) {
                        mob.getMoveControl().setWantedPosition(target.getX(), target.getY() + target.getBbHeight() + 0.5,
                                target.getZ(), 1.0);
                    } else {
                        mob.getNavigation().moveTo(target, 1.0);
                    }
                }
            } else {
                mob.getNavigation().stop();
            }
        }
        if (pause > 0) {
            pause--;
            return;
        }
        int total = 0;
        for (int i = 0; i < moves.size(); i++) {
            if (usable(i, dist, sight, target)) {
                total += moves.get(i).aiWeight;
            }
        }
        if (total <= 0) {
            return;
        }
        int roll = mob.getRandom().nextInt(total);
        for (int i = 0; i < moves.size(); i++) {
            if (!usable(i, dist, sight, target)) {
                continue;
            }
            roll -= moves.get(i).aiWeight;
            if (roll < 0) {
                DevilAbility move = moves.get(i);
                mob.startMove(move, i, target);
                cooldowns[i] = (int) (move.cooldown() * spec.cooldownScale) + move.duration();
                pause = 8 + mob.getRandom().nextInt(spec.boss ? 12 : 24);
                return;
            }
        }
    }

    private boolean usable(int i, double dist, boolean sight, LivingEntity target) {
        DevilAbility m = moves.get(i);
        return cooldowns[i] <= 0 && dist >= m.aiMin && dist <= m.aiMax && (sight || !m.needsSight)
                && m.aiReady(mob, target);
    }
}
