package com.csm.hybrids.contract;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.hybrid.HybridData;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;

/**
 * A move borrowed from a contract devil. It works in any form (a contractor is usually just a human) and costs no
 * blood: the devil takes its own price ({@link #price()}), paid when the move starts.
 */
public abstract class ContractAbility extends Ability {
    public final Contract contract;
    /** How far the crosshair picks the move's target. */
    protected double reach = 24;
    /** Health the devil eats when the move is used (the Fox Devil is paid in flesh). Never kills. */
    protected float fleshPrice;

    protected ContractAbility(Contract contract, String id) {
        super(contract.devil, id);
        this.contract = contract;
        anyForm();
    }

    protected ContractAbility reach(double reach) {
        this.reach = reach;
        return this;
    }

    protected ContractAbility flesh(float hp) {
        this.fleshPrice = hp;
        return this;
    }

    @Override
    public Component price() {
        return Component.translatable("price.csm." + id);
    }

    @Override
    public int wheelColor() {
        return contract.color;
    }

    @Override
    public boolean consumesBloodOnStart() {
        return false;
    }

    @Override
    public String checkUse(ServerPlayer player, HybridData data) {
        if (!data.hasContract(contract)) {
            return "msg.csm.contract_missing";
        }
        return null;
    }

    @Override
    public void start(ServerPlayer player, HybridData data, AbilityRun run) {
        if (fleshPrice > 0 && !player.getAbilities().instabuild) {
            // the devil takes its bite of you (set directly: invulnerability frames can't dodge a price)
            float take = Math.min(fleshPrice, player.getHealth() - 1f);
            if (take > 0) {
                player.setHealth(player.getHealth() - take);
                AbilityUtil.blood(player.serverLevel(), player.position().add(0, 1.2, 0), 10, 0.2);
            }
        }
        EntityHitResult hit = AbilityUtil.raycastEntity(player, reach);
        if (hit != null && hit.getEntity() instanceof LivingEntity target) {
            run.target = target;
        }
    }

    @Override
    public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
        perform(player, data, run);
    }

    protected abstract void perform(ServerPlayer player, HybridData data, AbilityRun run);

    /** The move's target if it is still alive. */
    protected static LivingEntity target(AbilityRun run) {
        return run.target instanceof LivingEntity l && l.isAlive() ? l : null;
    }
}
