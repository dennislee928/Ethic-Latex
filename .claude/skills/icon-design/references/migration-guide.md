# Icon Migration Guide

Migrate from legacy icon libraries to modern alternatives.

## Font Awesome → Lucide/Phosphor

### Common Mappings

| Font Awesome | Lucide | Phosphor |
|--------------|--------|----------|
| `fa-home` | `Home` | `House` |
| `fa-user` | `User` | `User` |
| `fa-users` | `Users` | `Users` |
| `fa-cog` / `fa-gear` | `Settings` | `Gear` |
| `fa-search` | `Search` | `MagnifyingGlass` |
| `fa-envelope` | `Mail` | `Envelope` |
| `fa-phone` | `Phone` | `Phone` |
| `fa-map-marker` | `MapPin` | `MapPin` |
| `fa-check` | `Check` | `Check` |
| `fa-times` / `fa-close` | `X` | `X` |
| `fa-plus` | `Plus` | `Plus` |
| `fa-minus` | `Minus` | `Minus` |
| `fa-trash` | `Trash2` | `Trash` |
| `fa-edit` / `fa-pencil` | `Pencil` | `Pencil` |
| `fa-star` | `Star` | `Star` |
| `fa-heart` | `Heart` | `Heart` |
| `fa-bell` | `Bell` | `Bell` |
| `fa-calendar` | `Calendar` | `Calendar` |
| `fa-clock` | `Clock` | `Clock` |
| `fa-file` | `File` | `File` |
| `fa-folder` | `Folder` | `Folder` |
| `fa-download` | `Download` | `Download` |
| `fa-upload` | `Upload` | `Upload` |
| `fa-share` | `Share2` | `Share` |
| `fa-link` | `Link` | `Link` |
| `fa-lock` | `Lock` | `Lock` |
| `fa-unlock` | `Unlock` | `LockOpen` |
| `fa-eye` | `Eye` | `Eye` |
| `fa-eye-slash` | `EyeOff` | `EyeSlash` |
| `fa-bars` | `Menu` | `List` |
| `fa-arrow-right` | `ArrowRight` | `ArrowRight` |
| `fa-arrow-left` | `ArrowLeft` | `ArrowLeft` |
| `fa-chevron-down` | `ChevronDown` | `CaretDown` |
| `fa-chevron-up` | `ChevronUp` | `CaretUp` |
| `fa-external-link` | `ExternalLink` | `ArrowSquareOut` |
| `fa-shopping-cart` | `ShoppingCart` | `ShoppingCart` |
| `fa-credit-card` | `CreditCard` | `CreditCard` |
| `fa-dollar` | `DollarSign` | `CurrencyDollar` |
| `fa-percent` | `Percent` | `Percent` |
| `fa-tag` | `Tag` | `Tag` |
| `fa-gift` | `Gift` | `Gift` |
| `fa-trophy` | `Trophy` | `Trophy` |
| `fa-shield` | `Shield` | `Shield` |
| `fa-bolt` / `fa-lightning` | `Zap` | `Lightning` |
| `fa-spinner` | `Loader2` | `CircleNotch` |

### Font Awesome Styles → Modern Equivalents

| FA Style | Lucide | Heroicons | Phosphor |
|----------|--------|-----------|----------|
| `fa-regular` (outline) | Default | `/24/outline` | `weight="regular"` |
| `fa-solid` | N/A | `/24/solid` | `weight="fill"` |
| `fa-light` | N/A | N/A | `weight="light"` |
| `fa-thin` | N/A | N/A | `weight="thin"` |
| `fa-duotone` | N/A | N/A | `weight="duotone"` |

---

## Material Icons → Lucide/Phosphor

### Common Mappings

| Material Icon | Lucide | Phosphor |
|---------------|--------|----------|
| `home` | `Home` | `House` |
| `person` | `User` | `User` |
| `people` / `group` | `Users` | `Users` |
| `settings` | `Settings` | `Gear` |
| `search` | `Search` | `MagnifyingGlass` |
| `mail` / `email` | `Mail` | `Envelope` |
| `phone` | `Phone` | `Phone` |
| `place` / `location_on` | `MapPin` | `MapPin` |
| `check` | `Check` | `Check` |
| `close` | `X` | `X` |
| `add` | `Plus` | `Plus` |
| `remove` | `Minus` | `Minus` |
| `delete` | `Trash2` | `Trash` |
| `edit` | `Pencil` | `Pencil` |
| `star` | `Star` | `Star` |
| `favorite` | `Heart` | `Heart` |
| `notifications` | `Bell` | `Bell` |
| `event` / `calendar_today` | `Calendar` | `Calendar` |
| `schedule` / `access_time` | `Clock` | `Clock` |
| `description` | `FileText` | `FileText` |
| `folder` | `Folder` | `Folder` |
| `file_download` | `Download` | `Download` |
| `file_upload` | `Upload` | `Upload` |
| `share` | `Share2` | `Share` |
| `link` | `Link` | `Link` |
| `lock` | `Lock` | `Lock` |
| `lock_open` | `Unlock` | `LockOpen` |
| `visibility` | `Eye` | `Eye` |
| `visibility_off` | `EyeOff` | `EyeSlash` |
| `menu` | `Menu` | `List` |
| `arrow_forward` | `ArrowRight` | `ArrowRight` |
| `arrow_back` | `ArrowLeft` | `ArrowLeft` |
| `expand_more` | `ChevronDown` | `CaretDown` |
| `expand_less` | `ChevronUp` | `CaretUp` |
| `open_in_new` | `ExternalLink` | `ArrowSquareOut` |
| `shopping_cart` | `ShoppingCart` | `ShoppingCart` |
| `credit_card` | `CreditCard` | `CreditCard` |
| `attach_money` | `DollarSign` | `CurrencyDollar` |
| `local_offer` | `Tag` | `Tag` |
| `card_giftcard` | `Gift` | `Gift` |
| `emoji_events` | `Trophy` | `Trophy` |
| `security` | `Shield` | `Shield` |
| `flash_on` / `bolt` | `Zap` | `Lightning` |
| `autorenew` / `sync` | `RefreshCw` | `ArrowsClockwise` |

---

## Feather Icons → Lucide

Lucide is a direct fork of Feather Icons with the same naming:

| Feather | Lucide |
|---------|--------|
| `feather-home` | `Home` |
| `feather-user` | `User` |
| `feather-settings` | `Settings` |
| ... | (same names, PascalCase) |

**Migration is straightforward:**
```tsx
// Before (Feather)
import { Home, User, Settings } from 'feather-icons-react'

// After (Lucide)
import { Home, User, Settings } from 'lucide-react'
```

---

## Emoji → Icons

**Never use emoji for UI icons.** Replace with proper icon components:

| Emoji | Lucide | Heroicons | Phosphor |
|-------|--------|-----------|----------|
| ✅ | `Check` | `check` | `Check` |
| ❌ | `X` | `x-mark` | `X` |
| ⚠️ | `AlertTriangle` | `exclamation-triangle` | `Warning` |
| ℹ️ | `Info` | `information-circle` | `Info` |
| 📞 | `Phone` | `phone` | `Phone` |
| ✉️ | `Mail` | `envelope` | `Envelope` |
| 📍 | `MapPin` | `map-pin` | `MapPin` |
| 🔒 | `Lock` | `lock-closed` | `Lock` |
| ⚡ | `Zap` | `bolt` | `Lightning` |
| ⭐ | `Star` | `star` | `Star` |
| ❤️ | `Heart` | `heart` | `Heart` |
| 🏆 | `Trophy` | `trophy` | `Trophy` |
| 🎁 | `Gift` | `gift` | `Gift` |
| 🔔 | `Bell` | `bell` | `Bell` |
| 📅 | `Calendar` | `calendar` | `Calendar` |
| ⏰ | `Clock` | `clock` | `Clock` |
| 🔍 | `Search` | `magnifying-glass` | `MagnifyingGlass` |
| 👤 | `User` | `user` | `User` |
| 👥 | `Users` | `user-group` | `Users` |
| 🏠 | `Home` | `home` | `House` |
| ⚙️ | `Settings` | `cog-6-tooth` | `Gear` |

**Why icons over emoji:**
1. **Consistency** - Same style across all icons
2. **Accessibility** - Screen readers handle them better
3. **Styling** - Can change colour, size, stroke width
4. **Performance** - Tree-shakeable, no font loading
5. **Professional** - Emoji render differently across platforms
