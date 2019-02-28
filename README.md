Rocket.Chat notification Plugin for Icinga
==============

This plugin will allow you to send notifications from Icinga directly to your Rocket.Chat Server.

## Example usage

```
./notify_rocketchat.py --user icinga --password icinga --url "https://example.com" --channel general --message 'Test notification'
```

### Icinga Notification Command Definition

```
object NotificationCommand "Notify Rocket.Chat" {
    import "plugin-notification-command"
    command = [ PluginDir + "/notify_rocketchat.py" ]
    arguments += {
        "--channel" = "$notify_rocketchat_channel$"
        "--password" = "$notify_rocketchat_password$"
        "--url" = "$notify_rocketchat_url$"
        "--user" = "$notify_rocketchat_user$"
        "--message" = "$notify_rocketchat_message$"
    }
}
```

### Host Notification Message example

```
$notification.type$ $host.name$ is $host.state$ $icinga.long_date_time$ $host.output$
```

### Service Notification Message example

```
$notification.type$ $host.display_name$.$service.name$ is $service.state$ $icinga.long_date_time$ $service.output$
```
