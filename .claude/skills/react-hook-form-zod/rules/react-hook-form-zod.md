---
paths: "**/*.tsx", "**/*form*.ts", "**/*.ts"
---

# React Hook Form + Zod Corrections

## ALWAYS Set defaultValues

```typescript
/* ❌ Causes uncontrolled→controlled warning */
const { register } = useForm<FormData>({
  resolver: zodResolver(schema),
  // No defaultValues!
})

/* ✅ Always provide defaultValues */
const { register } = useForm<FormData>({
  resolver: zodResolver(schema),
  defaultValues: {
    name: '',
    email: '',
    age: undefined, // or appropriate default
  },
})
```

## useFieldArray: Use field.id as Key

```typescript
/* ❌ Using index causes infinite re-renders */
{fields.map((field, index) => (
  <input key={index} {...register(`items.${index}.name`)} />
))}

/* ✅ Use field.id */
{fields.map((field, index) => (
  <input key={field.id} {...register(`items.${index}.name`)} />
))}
```

## Controller: MUST Spread {...field}

```typescript
/* ❌ Field doesn't update */
<Controller
  name="status"
  control={control}
  render={({ field }) => (
    <Select value={field.value} onChange={field.onChange} />
  )}
/>

/* ✅ Spread all field props */
<Controller
  name="status"
  control={control}
  render={({ field }) => (
    <Select {...field} />
  )}
/>
```

## Nested Error Access

```typescript
/* ❌ May crash on undefined */
errors.address.street.message

/* ✅ Use optional chaining */
errors.address?.street?.message
```

## Server Validation Required

```typescript
/* ❌ Security vulnerability - client only */
const onSubmit = (data) => {
  await api.post('/users', data) // No server validation!
}

/* ✅ Validate on BOTH client and server */
// Client: useForm with zodResolver
// Server:
app.post('/users', async (c) => {
  const result = schema.safeParse(await c.req.json())
  if (!result.success) {
    return c.json({ errors: result.error.flatten() }, 400)
  }
})
```

## Show Server Errors with setError

```typescript
/* ✅ Display server validation errors */
const onSubmit = async (data) => {
  const response = await api.post('/users', data)
  if (!response.ok) {
    const { errors } = await response.json()
    // Set field-specific errors
    Object.entries(errors).forEach(([field, message]) => {
      setError(field, { message })
    })
  }
}
```

## Zod Refinement: Include path

```typescript
/* ❌ Error shows on form, not field */
const schema = z.object({
  password: z.string(),
  confirm: z.string(),
}).refine(d => d.password === d.confirm, {
  message: "Passwords don't match",
})

/* ✅ Include path for field placement */
const schema = z.object({
  password: z.string(),
  confirm: z.string(),
}).refine(d => d.password === d.confirm, {
  message: "Passwords don't match",
  path: ['confirm'], // Error shows on confirm field
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| No `defaultValues` | Always provide `defaultValues: { field: '' }` |
| `key={index}` in useFieldArray | `key={field.id}` |
| Partial field props | Spread `{...field}` |
| `errors.a.b.message` | `errors.a?.b?.message` |
| Client-only validation | Validate on server too |
| Missing refinement path | Add `path: ['fieldName']` |
