const MAX_AVATAR_BYTES = 2 * 1024 * 1024;
const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);

function avatarStorageKey(userId: string) {
  return `valley.profile.avatar.${userId}`;
}

export function loadProfileAvatar(userId: string) {
  return window.localStorage.getItem(avatarStorageKey(userId)) ?? '';
}

export function saveProfileAvatar(userId: string, dataUrl: string) {
  if (dataUrl) window.localStorage.setItem(avatarStorageKey(userId), dataUrl);
  else window.localStorage.removeItem(avatarStorageKey(userId));
  window.dispatchEvent(new CustomEvent('valley-profile-avatar-changed', {
    detail: { userId, dataUrl },
  }));
}

export async function readProfileAvatar(file: File) {
  if (!ALLOWED_TYPES.has(file.type)) {
    throw new Error('Use uma imagem JPG, PNG ou WebP.');
  }
  if (file.size > MAX_AVATAR_BYTES) {
    throw new Error('A foto deve ter no máximo 2 MB.');
  }
  return await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('Não foi possível ler a imagem.'));
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.readAsDataURL(file);
  });
}
