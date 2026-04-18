import React, { useMemo, useState } from "react";
import {
  Autocomplete,
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  IconButton,
  MenuItem,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import { Delete as DeleteIcon } from "@mui/icons-material";
import FormRow from "./FormRow.jsx";
import {
  toInputDateTimeValue,
  toInputDateValue,
} from "../../utils/datetime.js";

const CUSTOM_FIELD_TYPES = {
  STRING: "string",
  TEXT: "text",
  DATE: "date",
  DATETIME: "datetime",
  BOOL: "bool",
};

const CUSTOM_FIELD_LABELS = {
  string: "Строка",
  text: "Текст",
  date: "Дата",
  datetime: "Дата и время",
  bool: "Чекбокс",
};

const hasValue = (type, value) => {
  if (type === CUSTOM_FIELD_TYPES.BOOL) {
    return value === true || value === false;
  }

  return Boolean(value?.trim?.());
};

const normalizeTextValue = (value) => {
  const trimmed = value?.trim?.();
  return trimmed ? trimmed : null;
};

const buildPayloadItem = (field, value) => {
  const payloadItem = { custom_field_id: field.id };

  if (field.type === CUSTOM_FIELD_TYPES.STRING) {
    payloadItem.value_string = normalizeTextValue(value);
  } else if (field.type === CUSTOM_FIELD_TYPES.TEXT) {
    payloadItem.value_text = normalizeTextValue(value);
  } else if (field.type === CUSTOM_FIELD_TYPES.DATE) {
    payloadItem.value_date = value ? value : null;
  } else if (field.type === CUSTOM_FIELD_TYPES.DATETIME) {
    payloadItem.value_datetime = value ? new Date(value).toISOString() : null;
  } else if (field.type === CUSTOM_FIELD_TYPES.BOOL) {
    payloadItem.value_bool = value ? value : null;
  }

  return payloadItem;
};

const TaskCustomFieldsSection = ({
  fields,
  activeFieldIds,
  values,
  onChange,
  onRemoveField,
  onAddExistingField,
  onCreateField,
  onDeleteFieldDefinition,
  creatingField,
}) => {
  const [showAddFieldForm, setShowAddFieldForm] = useState(false);
  const [newFieldName, setNewFieldName] = useState("");
  const [newFieldType, setNewFieldType] = useState(CUSTOM_FIELD_TYPES.STRING);

  const activeFields = useMemo(
    () => fields.filter((field) => activeFieldIds.includes(field.id)),
    [fields, activeFieldIds],
  );

  const availableOptions = useMemo(
    () =>
      fields
        .filter((field) => !activeFieldIds.includes(field.id))
        .map((field) => ({ ...field })),
    [fields, activeFieldIds],
  );

  const selectedExistingField = useMemo(
    () =>
      availableOptions.find(
        (option) =>
          option.name.toLowerCase() === newFieldName.trim().toLowerCase(),
      ) || null,
    [availableOptions, newFieldName],
  );

  const handleAddField = async () => {
    const normalizedName = newFieldName.trim();
    if (!normalizedName) {
      return;
    }

    if (selectedExistingField) {
      onAddExistingField?.(selectedExistingField.id);
      setNewFieldName("");
      setNewFieldType(CUSTOM_FIELD_TYPES.STRING);
      setShowAddFieldForm(false);
      return;
    }

    const createdField = await onCreateField?.({
      name: normalizedName,
      type: newFieldType,
    });

    if (createdField) {
      setNewFieldName("");
      setNewFieldType(CUSTOM_FIELD_TYPES.STRING);
      setShowAddFieldForm(false);
    }
  };

  return (
    <Box sx={{ px: 1.5, py: 1, fontFamily: '"Montserrat", sans-serif' }}>
      <Box sx={{ display: "grid", gap: 1 }}>
        {activeFields.map((field) => {
          const value = values[field.id] ?? "";

          if (field.type === CUSTOM_FIELD_TYPES.TEXT) {
            return (
              <FormRow key={field.id} label={field.name}>
                <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}>
                  <TextField
                    value={value}
                    onChange={(e) => onChange(field.id, e.target.value)}
                    variant="outlined"
                    size="small"
                    fullWidth
                    multiline
                    rows={4}
                    placeholder="Введите значение"
                    sx={{ fontFamily: '"Montserrat", sans-serif' }}
                  />
                  <IconButton
                    onClick={() => onRemoveField?.(field.id)}
                    size="small"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </FormRow>
            );
          }

          if (field.type === CUSTOM_FIELD_TYPES.DATE) {
            return (
              <FormRow key={field.id} label={field.name}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TextField
                    type="date"
                    value={value}
                    onChange={(e) => onChange(field.id, e.target.value)}
                    variant="outlined"
                    size="small"
                    fullWidth
                    sx={{ fontFamily: '"Montserrat", sans-serif' }}
                  />
                  <IconButton
                    onClick={() => onRemoveField?.(field.id)}
                    size="small"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </FormRow>
            );
          }

          if (field.type === CUSTOM_FIELD_TYPES.DATETIME) {
            return (
              <FormRow key={field.id} label={field.name}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TextField
                    type="datetime-local"
                    value={value}
                    onChange={(e) => onChange(field.id, e.target.value)}
                    variant="outlined"
                    size="small"
                    fullWidth
                    sx={{ fontFamily: '"Montserrat", sans-serif' }}
                  />
                  <IconButton
                    onClick={() => onRemoveField?.(field.id)}
                    size="small"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </FormRow>
            );
          }

          if (field.type === CUSTOM_FIELD_TYPES.BOOL) {
            return (
              <FormRow key={field.id} label={field.name}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <FormControl fullWidth size="small">
                    <FormControlLabel
                      sx={{ m: 0, fontFamily: '"Montserrat", sans-serif' }}
                      control={
                        <Checkbox
                          checked={value === true}
                          onChange={(e) => onChange(field.id, e.target.checked)}
                        />
                      }
                      label=""
                    />
                  </FormControl>
                  <IconButton
                    onClick={() => onRemoveField?.(field.id)}
                    size="small"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </FormRow>
            );
          }

          return (
            <FormRow key={field.id} label={field.name}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <TextField
                  value={value}
                  onChange={(e) => onChange(field.id, e.target.value)}
                  variant="outlined"
                  size="small"
                  fullWidth
                  placeholder="Введите значение"
                  sx={{ fontFamily: '"Montserrat", sans-serif' }}
                />
                <IconButton
                  onClick={() => onRemoveField?.(field.id)}
                  size="small"
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Box>
            </FormRow>
          );
        })}
      </Box>

      {!showAddFieldForm ? (
        <Button
          sx={{ mt: 1, fontFamily: '"Montserrat", sans-serif' }}
          variant="outlined"
          onClick={() => setShowAddFieldForm(true)}
        >
          Добавить поле
        </Button>
      ) : (
        <Box sx={{ mt: 1, display: "grid", gap: 1 }}>
          <Autocomplete
            freeSolo
            options={availableOptions}
            getOptionLabel={(option) =>
              typeof option === "string" ? option : option.name
            }
            inputValue={newFieldName}
            onInputChange={(_, value) => {
              setNewFieldName(value);
              const matched = availableOptions.find(
                (option) =>
                  option.name.toLowerCase() === value.trim().toLowerCase(),
              );
              if (matched) {
                setNewFieldType(matched.type);
              }
            }}
            onChange={(_, value) => {
              if (!value || typeof value === "string") {
                return;
              }

              setNewFieldName(value.name);
              setNewFieldType(value.type);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                size="small"
                placeholder="Название поля"
                sx={{ fontFamily: '"Montserrat", sans-serif' }}
              />
            )}
            renderOption={(props, option) => (
              <Box
                component="li"
                {...props}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 1,
                  fontFamily: '"Montserrat", sans-serif',
                }}
              >
                <Typography sx={{ fontFamily: '"Montserrat", sans-serif' }}>
                  {option.name}
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      color: "text.secondary",
                      fontFamily: '"Montserrat", sans-serif',
                    }}
                  >
                    {CUSTOM_FIELD_LABELS[option.type] || option.type}
                  </Typography>
                  <IconButton
                    size="small"
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      onDeleteFieldDefinition?.(option.id);
                    }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
            )}
          />

          <Select
            variant="outlined"
            size="small"
            value={newFieldType}
            onChange={(e) => setNewFieldType(e.target.value)}
            disabled={Boolean(selectedExistingField)}
            sx={{ fontFamily: '"Montserrat", sans-serif' }}
          >
            <MenuItem
              value={CUSTOM_FIELD_TYPES.STRING}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              {CUSTOM_FIELD_LABELS.string}
            </MenuItem>
            <MenuItem
              value={CUSTOM_FIELD_TYPES.TEXT}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              {CUSTOM_FIELD_LABELS.text}
            </MenuItem>
            <MenuItem
              value={CUSTOM_FIELD_TYPES.DATE}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              {CUSTOM_FIELD_LABELS.date}
            </MenuItem>
            <MenuItem
              value={CUSTOM_FIELD_TYPES.DATETIME}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              {CUSTOM_FIELD_LABELS.datetime}
            </MenuItem>
            <MenuItem
              value={CUSTOM_FIELD_TYPES.BOOL}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              {CUSTOM_FIELD_LABELS.bool}
            </MenuItem>
          </Select>

          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              onClick={handleAddField}
              disabled={!newFieldName.trim() || creatingField}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              {creatingField ? "Создание..." : "Добавить поле"}
            </Button>
            <Button
              onClick={() => {
                setShowAddFieldForm(false);
                setNewFieldName("");
                setNewFieldType(CUSTOM_FIELD_TYPES.STRING);
              }}
              sx={{ fontFamily: '"Montserrat", sans-serif' }}
            >
              Отмена
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
};

TaskCustomFieldsSection.buildInitialCustomFieldValues = (
  fields,
  taskCustomFieldValues = [],
) => {
  const initial = {};

  fields.forEach((field) => {
    const existing = taskCustomFieldValues.find(
      (item) => item.custom_field_id === field.id,
    );

    if (field.type === CUSTOM_FIELD_TYPES.STRING) {
      initial[field.id] = existing?.value_string ?? "";
    } else if (field.type === CUSTOM_FIELD_TYPES.TEXT) {
      initial[field.id] = existing?.value_text ?? "";
    } else if (field.type === CUSTOM_FIELD_TYPES.DATE) {
      initial[field.id] = toInputDateValue(existing?.value_date);
    } else if (field.type === CUSTOM_FIELD_TYPES.DATETIME) {
      initial[field.id] = toInputDateTimeValue(existing?.value_datetime);
    } else if (field.type === CUSTOM_FIELD_TYPES.BOOL) {
      initial[field.id] = existing?.value_bool;
    }
  });

  return initial;
};

TaskCustomFieldsSection.buildCustomFieldsPayload = (
  fields,
  values,
  initialValues,
  activeFieldIds,
  initialActiveFieldIds,
) => {
  const fieldsById = new Map(fields.map((field) => [field.id, field]));
  const payload = [];

  activeFieldIds.forEach((fieldId) => {
    const field = fieldsById.get(fieldId);
    if (!field) {
      return;
    }

    const currentValue = values[fieldId] ?? "";
    const initialValue = initialValues[fieldId] ?? "";
    const wasInitiallyActive = initialActiveFieldIds.includes(fieldId);

    if (!wasInitiallyActive) {
      payload.push(buildPayloadItem(field, currentValue));
      return;
    }

    if (
      !hasValue(field.type, currentValue) &&
      !hasValue(field.type, initialValue)
    ) {
      return;
    }

    payload.push(buildPayloadItem(field, currentValue));
  });

  return payload;
};

export default TaskCustomFieldsSection;
