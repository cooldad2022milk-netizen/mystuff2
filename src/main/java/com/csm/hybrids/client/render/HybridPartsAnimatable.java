package com.csm.hybrids.client.render;

import com.csm.hybrids.client.ClientHybridState;
import com.csm.hybrids.hybrid.HybridType;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;
import software.bernie.geckolib.util.RenderUtils;

/**
 * The GeckoLib side of one player's devil parts (head, arms, legs...). One instance per player.
 * <p>
 * Controllers:
 * <ul>
 *   <li>form - burst out (emerge), idle loop, retract</li>
 *   <li>chain - chainsaw only: chains crawl slowly at idle and scream round the bars while revving</li>
 *   <li>action - one-shot ability animations (plus the flamethrower flame loop)</li>
 *   <li>trigger - props of the manga trigger (cord handle snap-back, arrow drawn from the eye, grenade pin,
 *       spear drawn from the nape)</li>
 * </ul>
 */
public class HybridPartsAnimatable implements GeoAnimatable {
    private static final RawAnimation CHAIN_IDLE = RawAnimation.begin().thenLoop("chain_idle");
    private static final RawAnimation CHAIN_REV = RawAnimation.begin().thenLoop("chain_rev");
    private static final RawAnimation FLAME = RawAnimation.begin().thenLoop("flame");

    public final HybridType type;
    public final long instanceId;
    private final ClientHybridState state;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public HybridPartsAnimatable(HybridType type, ClientHybridState state) {
        this.type = type;
        this.state = state;
        this.instanceId = 0x5A5A0000L + state.playerId;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "form", 0, s -> {
            if (!state.formVisible(state.renderNow)) {
                return PlayState.STOP;
            }
            return s.setAndContinue(state.formAnim);
        }));

        if (type == HybridType.CHAINSAW) {
            controllers.add(new AnimationController<>(this, "chain", 0, s -> {
                if (!state.formVisible(state.renderNow)) {
                    return PlayState.STOP;
                }
                return s.setAndContinue(state.revving(state.renderNow) ? CHAIN_REV : CHAIN_IDLE);
            }));
        }

        AnimationController<HybridPartsAnimatable> action = new AnimationController<>(this, "action", 2, s -> {
            if (type == HybridType.FLAMETHROWER && state.fxActive("flame", state.renderNow)) {
                return s.setAndContinue(FLAME);
            }
            return PlayState.STOP;
        });
        for (String anim : actionAnims(type)) {
            action.triggerableAnim(anim, RawAnimation.begin().thenPlay(anim));
        }
        controllers.add(action);

        AnimationController<HybridPartsAnimatable> trigger = new AnimationController<>(this, "trigger", 0, s -> PlayState.STOP);
        switch (type) {
            case CHAINSAW -> trigger.triggerableAnim("cord_snap", RawAnimation.begin().thenPlay("cord_snap"));
            case CROSSBOW -> trigger.triggerableAnim("pull_arrow", RawAnimation.begin().thenPlay("pull_arrow"));
            case BOMB -> trigger.triggerableAnim("pull_pin", RawAnimation.begin().thenPlay("pull_pin"));
            case SPEAR -> trigger.triggerableAnim("pull_spear", RawAnimation.begin().thenPlay("pull_spear"));
            case KATANA, LONGSWORD -> trigger.triggerableAnim("pull_hand", RawAnimation.begin().thenPlay("pull_hand"));
            case VIOLENCE -> trigger.triggerableAnim("unmask", RawAnimation.begin().thenPlay("unmask"));
            default -> {
                if (type.humanoid) {
                    trigger.triggerableAnim("unleash", RawAnimation.begin().thenPlay("unleash"));
                }
            }
        }
        controllers.add(trigger);
    }

    public static String[] actionAnims(HybridType type) {
        return switch (type) {
            case CHAINSAW -> new String[]{"slash", "roar", "headbutt", "rip", "leg_spin", "throw", "drink"};
            case CROSSBOW -> new String[]{"volley", "charge", "storm", "flash", "drink"};
            case FLAMETHROWER -> new String[]{"napalm", "burst", "regen", "drink"};
            case WHIP -> new String[]{"lash", "storm", "snare", "swing", "crack", "drink"};
            case BOMB -> new String[]{"combo", "flick", "propulsion", "torpedo", "headless", "drink"};
            case SPEAR -> new String[]{"thrust", "throw", "volley", "impale", "eruption", "drink"};
            case KATANA -> new String[]{"iai", "twin", "flurry", "stance", "drink"};
            case LONGSWORD -> new String[]{"cleave", "whirl", "lunge", "guard", "drink"};
            case BLOOD -> new String[]{"hammer", "spear", "scythe", "control", "rain", "drink"};
            case SHARK -> new String[]{"swim", "bite", "ambush", "sharkform", "scent", "drink"};
            case VIOLENCE -> new String[]{"punch", "kick", "mouth_arm", "rampage", "drink"};
            case COSMOS -> new String[]{"halloween", "all_out", "knowledge", "collapse", "drink"};
            case GUN -> new String[]{"burst", "headshot", "storm", "massacre", "drink"};
            case NONE -> new String[0];
            default -> type.abilities().stream().map(com.csm.hybrids.ability.Ability::geoAnim).filter(g -> !g.isEmpty())
                    .distinct().toArray(String[]::new);
        };
    }

    public void trigger(String controller, String anim) {
        AnimatableManager<HybridPartsAnimatable> manager = cache.getManagerForId(instanceId);
        AnimationController<HybridPartsAnimatable> c = manager.getAnimationControllers().get(controller);
        if (c != null) {
            c.tryTriggerAnimation(anim);
        }
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public double getTick(Object object) {
        return RenderUtils.getCurrentTick();
    }
}
